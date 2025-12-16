"""
COMPLETE: Batch Tokenization with Level 1 Storage
Saves compact tokens to jobs.tokens (JSON column)

Run BEFORE this script:
    mysql -u root -p job_market_intelligence_platform < migration_level1_storage.sql

Usage:
    python scripts/batch_tokenize_jobs.py
    python scripts/batch_tokenize_jobs.py --batch-size 50
    python scripts/batch_tokenize_jobs.py --reprocess
"""

import sys
import os
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import argparse
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.services.preprocessing.tokenizers import (
    JobTitleTokenizerEnhanced,
    SkillTokenizer,
    DescriptionTokenizer,
    LocationTokenizer,
    ResponsibilityTokenizer,
    QualificationTokenizer,
    BenefitTokenizer,
)


def prepare_compact_tokens(tokens: dict) -> dict:
    """
    Prepare compact tokens for Level 1 storage (~500 bytes)
    
    Args:
        tokens: Full tokenization result
        
    Returns:
        Compact token dictionary
    """
    compact = {}
    
    # 1. Title
    if tokens.get('title'):
        title = tokens['title']
        recon = title.get('level_reconciliation', {})
        
        compact['title'] = {
            'level': title.get('level'),
            'role': title.get('role'),
            'confidence': round(recon.get('confidence', 0), 2),
            'has_discrepancy': recon.get('has_discrepancy', False)
        }
    
    # 2. Skills - Top 10 only
    if tokens.get('skills'):
        skills = tokens['skills']
        
        top_skills = []
        if skills.get('skills'):
            top_skills = [
                s.get('normalized') 
                for s in skills.get('skills', [])[:10]
                if s.get('normalized')
            ]
        
        compact['skills'] = {
            'count': skills.get('total_count', 0),
            'top': top_skills,
            'categories': skills.get('categories', [])[:5]
        }
    
    # 3. Location
    if tokens.get('location'):
        loc = tokens['location']
        
        compact['location'] = {
            'city': loc.get('city'),
            'province': loc.get('province'),
            'remote': loc.get('is_remote', False)
        }
    
    # 4. Experience & Education
    if tokens.get('qualifications'):
        qual = tokens['qualifications']
        
        if qual.get('experience'):
            compact['experience'] = {
                'years': qual['experience'].get('years', 0)
            }
        
        if qual.get('education'):
            compact['education'] = qual['education']
    
    # 5. Summary Stats
    compact['stats'] = {
        'has_description': bool(tokens.get('description')),
        'has_responsibilities': bool(tokens.get('responsibilities')),
        'has_qualifications': bool(tokens.get('qualifications')),
        'has_benefits': bool(tokens.get('benefits')),
        'completeness': calculate_completeness(tokens)
    }
    
    # 6. Metadata
    compact['meta'] = {
        'processed_at': datetime.now().isoformat()[:19],
        'has_errors': len(tokens.get('errors', [])) > 0
    }
    
    return compact


def calculate_completeness(tokens: dict) -> float:
    """Calculate data completeness score (0-1)"""
    fields = [
        'title', 'skills', 'location', 'description',
        'responsibilities', 'qualifications', 'benefits'
    ]
    
    present = sum(1 for field in fields if tokens.get(field))
    return round(present / len(fields), 2)


class BatchTokenizer:
    """Batch processing for job tokenization"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.db = SessionLocal()
        
        # Initialize tokenizers
        self.title_tokenizer = JobTitleTokenizerEnhanced()
        self.skill_tokenizer = SkillTokenizer()
        self.description_tokenizer = DescriptionTokenizer()
        self.location_tokenizer = LocationTokenizer()
        self.responsibility_tokenizer = ResponsibilityTokenizer()
        self.qualification_tokenizer = QualificationTokenizer()
        self.benefit_tokenizer = BenefitTokenizer()
        
        # Statistics
        self.stats = {
            'total_jobs': 0,
            'processed': 0,
            'errors': 0,
            'inconsistencies': 0,
            'needs_review': 0,
            'saved': 0,
            'save_errors': 0,
        }
    
    def get_total_jobs(self, reprocess: bool = False) -> int:
        """Get total number of jobs to process"""
        if reprocess:
            query = "SELECT COUNT(*) FROM jobs"
        else:
            query = "SELECT COUNT(*) FROM jobs WHERE is_tokenized = FALSE OR is_tokenized IS NULL"
        
        result = self.db.execute(text(query)).scalar()
        return result or 0
    
    def get_jobs_batch(self, offset: int, limit: int, reprocess: bool = False):
        """Get batch of jobs"""
        if reprocess:
            query = text("""
                SELECT id, judul, perusahaan, lokasi, level, 
                       deskripsi_singkat, tanggung_jawab, kualifikasi, 
                       keahlian, benefit
                FROM jobs 
                ORDER BY id 
                LIMIT :limit OFFSET :offset
            """)
        else:
            query = text("""
                SELECT id, judul, perusahaan, lokasi, level, 
                       deskripsi_singkat, tanggung_jawab, kualifikasi, 
                       keahlian, benefit
                FROM jobs 
                WHERE is_tokenized = FALSE OR is_tokenized IS NULL
                ORDER BY id 
                LIMIT :limit OFFSET :offset
            """)
        
        result = self.db.execute(query, {'limit': limit, 'offset': offset})
        return result.fetchall()
    
    def tokenize_job(self, job) -> dict:
        """Tokenize single job"""
        result = {
            'job_id': job.id,
            'title': None,
            'skills': None,
            'description': None,
            'location': None,
            'responsibilities': None,
            'qualifications': None,
            'benefits': None,
            'errors': []
        }
        
        # 1. Job Title
        try:
            if job.judul:
                title_result = self.title_tokenizer.tokenize_with_reconciliation(
                    title=job.judul,
                    db_level=job.level
                )
                result['title'] = title_result
                
                if title_result['level_reconciliation']['has_discrepancy']:
                    self.stats['inconsistencies'] += 1
                
                if title_result['level_reconciliation']['needs_review']:
                    self.stats['needs_review'] += 1
        except Exception as e:
            result['errors'].append(f"Title: {str(e)}")
        
        # 2. Skills
        try:
            if job.keahlian:
                result['skills'] = self.skill_tokenizer.tokenize(job.keahlian)
        except Exception as e:
            result['errors'].append(f"Skills: {str(e)}")
        
        # 3. Description
        try:
            if job.deskripsi_singkat:
                result['description'] = self.description_tokenizer.tokenize(job.deskripsi_singkat)
        except Exception as e:
            result['errors'].append(f"Description: {str(e)}")
        
        # 4. Location
        try:
            if job.lokasi:
                result['location'] = self.location_tokenizer.tokenize(job.lokasi)
        except Exception as e:
            result['errors'].append(f"Location: {str(e)}")
        
        # 5. Responsibilities
        try:
            if job.tanggung_jawab:
                result['responsibilities'] = self.responsibility_tokenizer.tokenize(job.tanggung_jawab)
        except Exception as e:
            result['errors'].append(f"Responsibilities: {str(e)}")
        
        # 6. Qualifications
        try:
            if job.kualifikasi:
                result['qualifications'] = self.qualification_tokenizer.tokenize(job.kualifikasi)
        except Exception as e:
            result['errors'].append(f"Qualifications: {str(e)}")
        
        # 7. Benefits
        try:
            if job.benefit:
                result['benefits'] = self.benefit_tokenizer.tokenize(job.benefit)
        except Exception as e:
            result['errors'].append(f"Benefits: {str(e)}")
        
        return result
    
    def save_tokens(self, job_id: int, tokens: dict):
        """
        Save Level 1 (Compact) tokens to jobs.tokens
        
        Args:
            job_id: Job ID
            tokens: Full tokenization result
        """
        try:
            # Prepare compact tokens
            compact = prepare_compact_tokens(tokens)
            
            # Save to database
            update_query = text("""
                UPDATE jobs 
                SET is_tokenized = TRUE,
                    tokens = :tokens,
                    tokenized_at = NOW(),
                    updated_at = NOW()
                WHERE id = :job_id
            """)
            
            self.db.execute(update_query, {
                'job_id': job_id,
                'tokens': json.dumps(compact, ensure_ascii=False)
            })
            self.db.commit()
            
            self.stats['saved'] += 1
            
        except Exception as e:
            self.db.rollback()
            self.stats['save_errors'] += 1
            print(f"  ❌ Save error for job {job_id}: {e}")
    
    def process_batch(self, offset: int, reprocess: bool = False):
        """Process one batch of jobs"""
        jobs = self.get_jobs_batch(offset, self.batch_size, reprocess)
        
        for job in jobs:
            try:
                # Tokenize job
                tokens = self.tokenize_job(job)
                
                # Save results
                self.save_tokens(job.id, tokens)
                
                # Update stats
                self.stats['processed'] += 1
                
                # Track errors
                if tokens['errors']:
                    self.stats['errors'] += len(tokens['errors'])
                    print(f"  ⚠ Job {job.id}: {len(tokens['errors'])} errors")
                
            except Exception as e:
                self.stats['errors'] += 1
                print(f"  ✗ Job {job.id}: Failed - {str(e)}")
    
    def run(self, reprocess: bool = False):
        """Run batch processing"""
        print("=" * 70)
        print("BATCH JOB TOKENIZATION")
        print("=" * 70)
        print()
        
        # Get total jobs
        total_jobs = self.get_total_jobs(reprocess)
        self.stats['total_jobs'] = total_jobs
        
        if total_jobs == 0:
            print("✓ No jobs to process!")
            return
        
        print(f"Total jobs to process: {total_jobs}")
        print(f"Batch size: {self.batch_size}")
        print(f"Estimated batches: {(total_jobs + self.batch_size - 1) // self.batch_size}")
        print()
        
        # Process in batches
        start_time = datetime.now()
        
        for offset in range(0, total_jobs, self.batch_size):
            batch_num = (offset // self.batch_size) + 1
            total_batches = (total_jobs + self.batch_size - 1) // self.batch_size
            
            print(f"Processing batch {batch_num}/{total_batches} (jobs {offset+1}-{min(offset+self.batch_size, total_jobs)})...")
            
            self.process_batch(offset, reprocess)
            
            # Progress
            progress = (self.stats['processed'] / total_jobs) * 100
            print(f"  Progress: {self.stats['processed']}/{total_jobs} ({progress:.1f}%)")
            print(f"  Saved: {self.stats['saved']} | Errors: {self.stats['errors']}")
            print()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 70)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 70)
        print()
        print(f"Total jobs:        {self.stats['total_jobs']}")
        print(f"Processed:         {self.stats['processed']}")
        print(f"Saved:             {self.stats['saved']}")
        print(f"Save errors:       {self.stats['save_errors']}")
        print(f"Tokenize errors:   {self.stats['errors']}")
        print(f"Inconsistencies:   {self.stats['inconsistencies']}")
        print(f"Needs review:      {self.stats['needs_review']}")
        print()
        print(f"Duration:          {duration:.2f} seconds")
        if duration > 0:
            print(f"Speed:             {self.stats['processed']/duration:.2f} jobs/second")
        print()
        
        if self.stats['needs_review'] > 0:
            print(f"⚠️  {self.stats['needs_review']} jobs flagged for review!")
            print("   Run: python scripts/generate_inconsistency_report.py")
        
        print("=" * 70)
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Batch tokenize jobs with storage')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size (default: 100)')
    parser.add_argument('--reprocess', action='store_true',
                       help='Reprocess all jobs (default: only unprocessed)')
    
    args = parser.parse_args()
    
    # Run batch processing
    processor = BatchTokenizer(batch_size=args.batch_size)
    processor.run(reprocess=args.reprocess)


if __name__ == "__main__":
    main()
