"""
Inconsistency Report Generator
Analyzes and reports data inconsistencies in job postings

Features:
- Detect level inconsistencies (title vs database)
- Generate detailed report
- Export to CSV
- Show statistics

Usage:
    python scripts/generate_inconsistency_report.py
    python scripts/generate_inconsistency_report.py --export report.csv
"""

import sys
import os
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import argparse
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import csv

from app.database import SessionLocal
from app.services.preprocessing.tokenizers.job_title_tokenizer_enhanced import JobTitleTokenizerEnhanced


class InconsistencyReporter:
    """Generate inconsistency reports"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.tokenizer = JobTitleTokenizerEnhanced()
        self.inconsistencies = []
    
    def get_all_jobs(self):
        """Get all jobs with title and level"""
        query = text("""
            SELECT id, judul, level, perusahaan, lokasi
            FROM jobs
            WHERE judul IS NOT NULL
            ORDER BY id
        """)
        return self.db.execute(query).fetchall()
    
    def analyze_job(self, job):
        """Analyze single job for inconsistencies"""
        result = self.tokenizer.tokenize_with_reconciliation(
            title=job.judul,
            db_level=job.level
        )
        
        recon = result['level_reconciliation']
        
        if recon['has_discrepancy']:
            inconsistency = {
                'job_id': job.id,
                'title': job.judul,
                'company': job.perusahaan,
                'location': job.lokasi,
                'db_level': recon['db_level'],
                'title_level': recon['title_level'],
                'final_level': recon['final_level'],
                'confidence': recon['confidence'],
                'needs_review': recon['needs_review'],
                'reason': recon['decision_reason']
            }
            return inconsistency
        
        return None
    
    def generate_report(self):
        """Generate full inconsistency report"""
        print("=" * 70)
        print("INCONSISTENCY REPORT GENERATOR")
        print("=" * 70)
        print()
        
        print("Fetching jobs...")
        jobs = self.get_all_jobs()
        total_jobs = len(jobs)
        
        print(f"Total jobs: {total_jobs}")
        print()
        print("Analyzing...")
        
        # Analyze each job
        for i, job in enumerate(jobs, 1):
            inconsistency = self.analyze_job(job)
            
            if inconsistency:
                self.inconsistencies.append(inconsistency)
            
            # Progress
            if i % 100 == 0:
                print(f"  Processed {i}/{total_jobs} jobs...")
        
        print(f"✓ Analysis complete!")
        print()
        
        # Statistics
        total_inconsistencies = len(self.inconsistencies)
        needs_review = sum(1 for inc in self.inconsistencies if inc['needs_review'])
        high_confidence = sum(1 for inc in self.inconsistencies if inc['confidence'] >= 0.75)
        
        print("=" * 70)
        print("STATISTICS")
        print("=" * 70)
        print()
        print(f"Total jobs analyzed:      {total_jobs}")
        print(f"Inconsistencies found:    {total_inconsistencies} ({total_inconsistencies/total_jobs*100:.1f}%)")
        print(f"High confidence issues:   {high_confidence}")
        print(f"Flagged for review:       {needs_review}")
        print()
        
        # Show top inconsistencies
        if self.inconsistencies:
            print("=" * 70)
            print("TOP 10 INCONSISTENCIES (Needs Review)")
            print("=" * 70)
            print()
            
            # Sort by confidence (high confidence = more certain it's wrong)
            sorted_inc = sorted(
                [inc for inc in self.inconsistencies if inc['needs_review']],
                key=lambda x: x['confidence'],
                reverse=True
            )
            
            for i, inc in enumerate(sorted_inc[:10], 1):
                print(f"{i}. Job ID: {inc['job_id']}")
                print(f"   Title: {inc['title']}")
                print(f"   Company: {inc['company']}")
                print(f"   DB Level: {inc['db_level']} → Title Level: {inc['title_level']}")
                print(f"   Confidence: {inc['confidence']:.0%}")
                print(f"   Decision: {inc['reason']}")
                print()
        
        print("=" * 70)
    
    def export_to_csv(self, filename: str):
        """Export inconsistencies to CSV"""
        if not self.inconsistencies:
            print("No inconsistencies to export!")
            return
        
        print(f"Exporting to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'job_id', 'title', 'company', 'location',
                'db_level', 'title_level', 'final_level',
                'confidence', 'needs_review', 'reason'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(self.inconsistencies)
        
        print(f"✓ Exported {len(self.inconsistencies)} records to {filename}")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Generate inconsistency report')
    parser.add_argument('--export', type=str, default=None,
                       help='Export to CSV file')
    
    args = parser.parse_args()
    
    # Generate report
    reporter = InconsistencyReporter()
    reporter.generate_report()
    
    # Export if requested
    if args.export:
        reporter.export_to_csv(args.export)


if __name__ == "__main__":
    main()
