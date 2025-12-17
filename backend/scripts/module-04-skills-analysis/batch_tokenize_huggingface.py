"""
Batch Tokenization for HuggingFace Dataset Creation
Processes raw job CSV and creates tokenized version with 38 columns

Author: Herlambang Haryo Putro
GitHub: https://github.com/herlambangharyoputro
Project: Job Market Intelligence Platform

Usage:
    python scripts/batch_tokenize_huggingface.py
    python scripts/batch_tokenize_huggingface.py --input data/raw/lokerid/loker_data.csv
    python scripts/batch_tokenize_huggingface.py --sample 100

Output:
    backend/outputs/huggingface/loker_data_tokenized.csv (38 columns)
"""

import sys
import os
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import argparse
import pandas as pd
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter


# =============================================================================
# SIMPLIFIED TOKENIZERS (Standalone - No Database Dependencies)
# =============================================================================

class TextCleaner:
    """Indonesian text cleaning and normalization"""
    
    def __init__(self):
        self.indonesian_stopwords = {
            'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'dengan', 'pada',
            'adalah', 'ini', 'itu', 'atau', 'juga', 'dalam', 'akan', 'dapat',
            'ada', 'oleh', 'sebagai', 'tidak', 'sudah', 'telah', 'hanya',
            'sangat', 'bisa', 'menjadi', 'lebih', 'saat', 'masih', 'setiap',
            'karena', 'jika', 'saya', 'anda', 'kita', 'mereka', 'kami'
        }
        
        self.slang_map = {
            'yg': 'yang', 'dgn': 'dengan', 'utk': 'untuk', 'tdk': 'tidak',
            'dg': 'dengan', 'pd': 'pada', 'hrs': 'harus', 'blm': 'belum',
            'krn': 'karena', 'sdh': 'sudah', 'spy': 'supaya', 'jgn': 'jangan',
            'tlg': 'tolong', 'org': 'orang', 'sm': 'sama', 'ama': 'sama',
            'jd': 'jadi', 'bnr': 'benar', 'dll': 'dan lain lain'
        }
    
    def clean(self, text: str) -> str:
        """Clean and normalize text"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text)
        
        # Normalize slang
        for slang, formal in self.slang_map.items():
            text = re.sub(r'\b' + slang + r'\b', formal, text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def tokenize(self, text: str, remove_stopwords: bool = False) -> List[str]:
        """Tokenize text into words"""
        text = self.clean(text).lower()
        
        # Extract words
        tokens = re.findall(r'\b\w+\b', text)
        
        # Remove stopwords if requested
        if remove_stopwords:
            tokens = [t for t in tokens if t not in self.indonesian_stopwords]
        
        # Filter short tokens
        tokens = [t for t in tokens if len(t) > 2]
        
        return tokens


class JobTitleTokenizer:
    """Job title tokenization with level extraction"""
    
    def __init__(self):
        self.cleaner = TextCleaner()
        
        self.level_keywords = {
            'intern': ['intern', 'magang', 'internship'],
            'entry': ['entry', 'junior', 'fresh graduate', 'pemula'],
            'mid': ['mid', 'staff', 'officer', 'associate'],
            'senior': ['senior', 'sr', 'lead', 'principal'],
            'manager': ['manager', 'manajer', 'supervisor', 'koordinator'],
            'director': ['director', 'direktur', 'head', 'kepala'],
            'executive': ['executive', 'vice president', 'vp', 'c-level', 'ceo', 'cto', 'cfo']
        }
    
    def extract_level(self, title: str) -> Optional[str]:
        """Extract job level from title"""
        title_lower = title.lower()
        
        for level, keywords in self.level_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return level
        
        return None
    
    def tokenize(self, title: str) -> Dict[str, Any]:
        """Tokenize job title"""
        if not title or pd.isna(title):
            return {
                'original': '',
                'cleaned': '',
                'tokens': [],
                'level_extracted': None
            }
        
        cleaned = self.cleaner.clean(title)
        tokens = self.cleaner.tokenize(cleaned, remove_stopwords=True)
        level = self.extract_level(title)
        
        return {
            'original': title,
            'cleaned': cleaned,
            'tokens': tokens,
            'level_extracted': level
        }


class SkillTokenizer:
    """Skills extraction and categorization"""
    
    def __init__(self):
        self.skill_categories = {
            'programming': {
                'python', 'java', 'javascript', 'typescript', 'php', 'ruby',
                'c', 'c++', 'c#', 'go', 'golang', 'rust', 'swift', 'kotlin',
                'scala', 'r', 'matlab'
            },
            'frontend': {
                'html', 'html5', 'css', 'css3', 'react', 'reactjs', 'react.js',
                'vue', 'vuejs', 'vue.js', 'angular', 'angularjs', 'svelte',
                'next.js', 'nextjs', 'nuxt', 'nuxtjs', 'jquery', 'bootstrap',
                'tailwind', 'tailwindcss', 'sass', 'scss', 'webpack'
            },
            'backend': {
                'node.js', 'nodejs', 'express', 'expressjs', 'nest.js', 'nestjs',
                'django', 'flask', 'fastapi', 'laravel', 'symfony', 'codeigniter',
                'spring', 'spring boot', 'rails', 'ruby on rails', '.net', 'asp.net'
            },
            'database': {
                'mysql', 'postgresql', 'postgres', 'sql server', 'mssql',
                'oracle', 'mongodb', 'mongo', 'redis', 'cassandra',
                'elasticsearch', 'sqlite', 'mariadb', 'dynamodb'
            },
            'cloud': {
                'aws', 'amazon web services', 'azure', 'microsoft azure',
                'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
                'jenkins', 'gitlab', 'github actions', 'terraform', 'ansible'
            },
            'data_science': {
                'pandas', 'numpy', 'tensorflow', 'keras', 'pytorch',
                'scikit-learn', 'sklearn', 'jupyter', 'tableau', 'power bi',
                'spark', 'hadoop', 'matplotlib', 'seaborn'
            },
            'soft_skills': {
                'communication', 'komunikasi', 'teamwork', 'kerja sama',
                'leadership', 'kepemimpinan', 'problem solving',
                'analytical', 'analitis', 'critical thinking'
            }
        }
    
    def parse_skills(self, text: str) -> List[str]:
        """Parse skills from text"""
        if not text or pd.isna(text):
            return []
        
        # Split by delimiters
        skills = re.split(r'[,;•·\n|]', str(text))
        skills = [s.strip() for s in skills if s.strip()]
        
        return skills
    
    def categorize_skill(self, skill: str) -> str:
        """Categorize a skill"""
        skill_lower = skill.lower()
        
        for category, skill_set in self.skill_categories.items():
            if skill_lower in skill_set:
                return category
        
        return 'other'
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """Tokenize skills"""
        skills = self.parse_skills(text)
        
        categorized = {}
        for skill in skills:
            category = self.categorize_skill(skill)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill)
        
        return {
            'original': text,
            'skills': skills,
            'total_count': len(skills),
            'unique_count': len(set([s.lower() for s in skills])),
            'categorized': categorized,
            'categories': list(categorized.keys())
        }


class LocationTokenizer:
    """Location parsing with city extraction"""
    
    def __init__(self):
        self.major_cities = {
            'jakarta', 'surabaya', 'bandung', 'medan', 'semarang',
            'makassar', 'palembang', 'tangerang', 'depok', 'bekasi',
            'bogor', 'batam', 'pekanbaru', 'bandar lampung', 'malang'
        }
        
        self.remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere']
    
    def is_remote(self, location: str) -> bool:
        """Check if location is remote"""
        if not location or pd.isna(location):
            return False
        
        location_lower = location.lower()
        return any(keyword in location_lower for keyword in self.remote_keywords)
    
    def extract_city(self, location: str) -> Optional[str]:
        """Extract city name"""
        if not location or pd.isna(location):
            return None
        
        location_lower = location.lower()
        
        for city in self.major_cities:
            if city in location_lower:
                return city.title()
        
        # Extract first word as potential city
        words = location.split(',')[0].strip().split()
        if words:
            return words[0]
        
        return None
    
    def tokenize(self, location: str) -> Dict[str, Any]:
        """Tokenize location"""
        return {
            'original': location if location and not pd.isna(location) else '',
            'city': self.extract_city(location),
            'is_remote': self.is_remote(location)
        }


# =============================================================================
# BATCH PROCESSOR
# =============================================================================

class HuggingFaceTokenizer:
    """Batch tokenizer for HuggingFace dataset creation"""
    
    def __init__(self):
        self.title_tokenizer = JobTitleTokenizer()
        self.skill_tokenizer = SkillTokenizer()
        self.location_tokenizer = LocationTokenizer()
        self.text_cleaner = TextCleaner()
    
    def process_dataset(self, input_csv: str, output_csv: str, sample_size: Optional[int] = None):
        """
        Process raw dataset and create tokenized version
        
        Args:
            input_csv: Path to raw CSV
            output_csv: Path to save processed CSV
            sample_size: Number of rows to process (None = all)
        """
        print("=" * 70)
        print("HUGGINGFACE DATASET TOKENIZATION")
        print("=" * 70)
        print()
        
        # Load data
        print("Loading data...")
        df = pd.read_csv(input_csv)
        
        if sample_size:
            df = df.head(sample_size)
            print(f"✓ Loaded {len(df)} records (sample)")
        else:
            print(f"✓ Loaded {len(df)} records (all)")
        print()
        
        # Process each row
        print("Processing records...")
        results = []
        
        for idx, row in df.iterrows():
            if idx % 100 == 0 and idx > 0:
                print(f"  Processed {idx}/{len(df)} records...")
            
            result_row = self.process_row(row)
            results.append(result_row)
        
        print(f"✓ Processed {len(results)} records")
        print()
        
        # Create output dataframe
        output_df = pd.DataFrame(results)
        
        # Save to CSV
        print(f"Saving to {output_csv}...")
        output_df.to_csv(output_csv, index=False, encoding='utf-8')
        print("✓ Saved successfully!")
        print()
        
        # Statistics
        self.print_statistics(output_df)
    
    def process_row(self, row: pd.Series) -> Dict[str, Any]:
        """Process single row"""
        
        # Tokenize title
        title_result = self.title_tokenizer.tokenize(row.get('judul', ''))
        
        # Tokenize skills
        skill_result = self.skill_tokenizer.tokenize(row.get('keahlian', ''))
        
        # Tokenize location
        location_result = self.location_tokenizer.tokenize(row.get('lokasi', ''))
        
        # Clean description
        desc_cleaned = self.text_cleaner.clean(row.get('deskripsi_singkat', ''))
        desc_tokens = self.text_cleaner.tokenize(desc_cleaned, remove_stopwords=True)
        
        # Clean responsibilities
        resp_cleaned = self.text_cleaner.clean(row.get('tanggung_jawab', ''))
        resp_tokens = self.text_cleaner.tokenize(resp_cleaned, remove_stopwords=True)
        
        # Clean qualifications
        qual_cleaned = self.text_cleaner.clean(row.get('kualifikasi', ''))
        qual_tokens = self.text_cleaner.tokenize(qual_cleaned, remove_stopwords=True)
        
        # Build result (38 columns)
        result = {
            # Original 20 columns
            'judul': row.get('judul', ''),
            'perusahaan': row.get('perusahaan', ''),
            'lokasi': row.get('lokasi', ''),
            'lokasi_detail': row.get('lokasi_detail', ''),
            'tipe_pekerjaan': row.get('tipe_pekerjaan', ''),
            'level': row.get('level', ''),
            'fungsi': row.get('fungsi', ''),
            'pendidikan': row.get('pendidikan', ''),
            'gaji': row.get('gaji', ''),
            'industri': row.get('industri', ''),
            'jumlah_karyawan': row.get('jumlah_karyawan', ''),
            'tanggal_posting': row.get('tanggal_posting', ''),
            'posting_relatif': row.get('posting_relatif', ''),
            'waktu_scraping': row.get('waktu_scraping', ''),
            'deskripsi_singkat': row.get('deskripsi_singkat', ''),
            'tanggung_jawab': row.get('tanggung_jawab', ''),
            'kualifikasi': row.get('kualifikasi', ''),
            'keahlian': row.get('keahlian', ''),
            'benefit': row.get('benefit', ''),
            'url': row.get('url', ''),
            
            # Title processing (3 columns)
            'title_cleaned': title_result['cleaned'],
            'title_tokens': json.dumps(title_result['tokens'], ensure_ascii=False),
            'title_level_extracted': title_result['level_extracted'] or '',
            
            # Skills processing (4 columns)
            'skills_list': json.dumps(skill_result['skills'], ensure_ascii=False),
            'skills_count': skill_result['total_count'],
            'skills_categories': json.dumps(skill_result['categories'], ensure_ascii=False),
            'skills_categorized': json.dumps(skill_result['categorized'], ensure_ascii=False),
            
            # Location processing (2 columns)
            'location_city': location_result['city'] or '',
            'location_is_remote': location_result['is_remote'],
            
            # Description processing (3 columns)
            'description_cleaned': desc_cleaned,
            'description_tokens': json.dumps(desc_tokens[:50], ensure_ascii=False),
            'description_length': len(desc_tokens),
            
            # Responsibility processing (3 columns)
            'responsibility_cleaned': resp_cleaned,
            'responsibility_tokens': json.dumps(resp_tokens[:50], ensure_ascii=False),
            'responsibility_length': len(resp_tokens),
            
            # Qualification processing (3 columns)
            'qualification_cleaned': qual_cleaned,
            'qualification_tokens': json.dumps(qual_tokens[:50], ensure_ascii=False),
            'qualification_length': len(qual_tokens),
        }
        
        return result
    
    def print_statistics(self, df: pd.DataFrame):
        """Print processing statistics"""
        print("=" * 70)
        print("PROCESSING STATISTICS")
        print("=" * 70)
        print(f"Total records: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print()
        
        print("Column breakdown:")
        print(f"  Original columns: 20")
        print(f"  Title processing: 3")
        print(f"  Skills processing: 4")
        print(f"  Location processing: 2")
        print(f"  Text processing: 9 (description, responsibility, qualification)")
        print(f"  Total: 38 columns")
        print()
        
        # Skills category distribution
        print("Skills category distribution:")
        all_categories = []
        for cats in df['skills_categories'].dropna():
            try:
                all_categories.extend(json.loads(cats))
            except:
                pass
        
        category_counts = Counter(all_categories)
        for category, count in category_counts.most_common():
            print(f"  {category}: {count}")
        print()
        
        # Level extraction success
        extracted_levels = df['title_level_extracted'].apply(lambda x: bool(x))
        print(f"Job level extraction:")
        print(f"  Successfully extracted: {extracted_levels.sum()} ({extracted_levels.sum()/len(df)*100:.1f}%)")
        print(f"  Not extracted: {(~extracted_levels).sum()} ({(~extracted_levels).sum()/len(df)*100:.1f}%)")
        print()
        
        # Remote jobs
        remote_count = df['location_is_remote'].sum()
        print(f"Remote jobs: {remote_count} ({remote_count/len(df)*100:.1f}%)")
        print()
        
        print("=" * 70)
        print("✅ HUGGINGFACE DATASET READY!")
        print("=" * 70)


def combine_csv_files(folder_path: Path) -> pd.DataFrame:
    """
    Combine all CSV files in a folder and remove duplicates
    
    Args:
        folder_path: Path to folder containing CSV files
        
    Returns:
        Combined DataFrame with duplicates removed
    """
    print("=" * 70)
    print("COMBINING CSV FILES")
    print("=" * 70)
    print()
    
    # Find all CSV files
    csv_files = list(folder_path.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    
    print(f"Found {len(csv_files)} CSV file(s):")
    for f in csv_files:
        file_size = f.stat().st_size / 1024  # KB
        print(f"  - {f.name} ({file_size:.1f} KB)")
    print()
    
    # Load and combine all files
    dfs = []
    total_rows = 0
    
    for csv_file in csv_files:
        print(f"Loading {csv_file.name}...")
        try:
            df = pd.read_csv(csv_file)
            rows = len(df)
            total_rows += rows
            dfs.append(df)
            print(f"  ✓ Loaded {rows:,} rows")
        except Exception as e:
            print(f"  ✗ Error loading {csv_file.name}: {e}")
    
    print()
    
    if not dfs:
        raise ValueError("No CSV files could be loaded")
    
    # Combine all dataframes
    print("Combining dataframes...")
    df_combined = pd.concat(dfs, ignore_index=True)
    print(f"✓ Combined total: {len(df_combined):,} rows")
    print()
    
    # Remove duplicates by URL
    print("Removing duplicates by URL...")
    initial_count = len(df_combined)
    
    if 'url' in df_combined.columns:
        df_combined = df_combined.drop_duplicates(subset=['url'], keep='last')
        duplicates_removed = initial_count - len(df_combined)
        print(f"✓ Removed {duplicates_removed:,} duplicate(s)")
        print(f"✓ Final dataset: {len(df_combined):,} unique rows")
    else:
        print("⚠ Warning: 'url' column not found, cannot deduplicate")
    
    print()
    print("=" * 70)
    print()
    
    return df_combined


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch tokenize jobs for HuggingFace dataset'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/raw/lokerid/loker_data_20251207_185522.csv',
        help='Input CSV file path (ignored if --combine-all is used)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='outputs/huggingface/loker_data_tokenized.csv',
        help='Output CSV file path'
    )
    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Process only N rows (for testing)'
    )
    parser.add_argument(
        '--combine-all',
        action='store_true',
        help='Combine all CSV files in lokerid folder'
    )
    parser.add_argument(
        '--folder',
        type=str,
        default='data/raw/lokerid',
        help='Folder containing CSV files (used with --combine-all)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths - Find backend root by looking for 'backend' in path
    script_path = Path(__file__).resolve()
    
    # Debug info
    print(f"Script location: {script_path}")
    print()
    
    # Navigate up until we find 'backend' directory
    backend_root = script_path.parent
    max_iterations = 10
    iterations = 0
    
    while backend_root.name != 'backend' and backend_root.parent != backend_root and iterations < max_iterations:
        backend_root = backend_root.parent
        iterations += 1
    
    if backend_root.name != 'backend':
        print(f"❌ Error: Could not find 'backend' directory")
        print(f"   Script is at: {script_path}")
        print(f"   Current search path: {backend_root}")
        print()
        print("Solution: Please run script from backend directory:")
        print("  cd job-market-intelligence-platform/backend")
        print("  python scripts/batch_tokenize_huggingface.py --combine-all")
        sys.exit(1)
    
    print(f"✓ Backend root: {backend_root}")
    print()
    
    output_path = backend_root / args.output
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle combine-all mode
    if args.combine_all:
        folder_path = backend_root / args.folder
        
        print(f"Mode: Combine all CSV files")
        print(f"Folder: {folder_path}")
        print(f"Output: {output_path}")
        if args.sample:
            print(f"Sample: {args.sample} rows")
        print()
        
        # Check folder exists
        if not folder_path.exists():
            print(f"❌ Error: Folder not found: {folder_path}")
            sys.exit(1)
        
        # Combine all CSV files
        try:
            df_combined = combine_csv_files(folder_path)
            
            # Save combined file temporarily
            combined_temp = output_path.parent / "combined_temp.csv"
            print(f"Saving combined file to: {combined_temp}")
            df_combined.to_csv(combined_temp, index=False, encoding='utf-8')
            print(f"✓ Saved {len(df_combined):,} rows")
            print()
            
            # Use combined file as input
            input_path = combined_temp
            
        except Exception as e:
            print(f"❌ Error combining files: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    else:
        # Single file mode
        input_path = backend_root / args.input
        
        print(f"Mode: Single file")
        print(f"Input:  {input_path}")
        print(f"Output: {output_path}")
        if args.sample:
            print(f"Sample: {args.sample} rows")
        print()
        
        # Check input exists
        if not input_path.exists():
            print(f"❌ Error: Input file not found: {input_path}")
            print()
            print("Available data files:")
            data_dir = backend_root / 'data' / 'raw' / 'lokerid'
            if data_dir.exists():
                for f in data_dir.glob('*.csv'):
                    print(f"  - {f.relative_to(backend_root)}")
            print()
            print("Tip: Use --combine-all to process all files in folder")
            sys.exit(1)
    
    # Process
    tokenizer = HuggingFaceTokenizer()
    tokenizer.process_dataset(
        str(input_path),
        str(output_path),
        sample_size=args.sample
    )
    
    # Cleanup temp file if it exists
    if args.combine_all:
        combined_temp = output_path.parent / "combined_temp.csv"
        if combined_temp.exists():
            combined_temp.unlink()
            print(f"✓ Cleaned up temporary file")
    
    print()
    print(f"✓ Dataset saved to: {output_path}")
    print()
    print("Next steps:")
    print("  1. Review the output CSV")
    print("  2. Copy to HuggingFace dataset folder:")
    print("     cp outputs/huggingface/loker_data_tokenized.csv \\")
    print("        ../huggingface_datasets/dataset2_tokenized/")
    print("  3. Upload to HuggingFace:")
    print("     - README.md")
    print("     - loker_data_tokenized.csv")
    print("     - indonesian_job_market_tokenized.py")


if __name__ == "__main__":
    main()