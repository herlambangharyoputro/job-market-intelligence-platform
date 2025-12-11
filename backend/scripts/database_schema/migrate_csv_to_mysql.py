"""
Script untuk migrasi data CSV ke MySQL
File: scripts/database_schema/migrate_csv_to_mysql.py
Run: python scripts/database_schema/migrate_csv_to_mysql.py
"""
import sys
import os
from pathlib import Path

# Add backend root to Python path
# Current file: backend/scripts/database_schema/migrate_csv_to_mysql.py
# We need: backend/
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session 

# Add parent directory to path for imports 

from app.database import SessionLocal, engine
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


class CSVMigrator:
    """Class untuk handle CSV to MySQL migration"""
    
    def __init__(self, data_dir: str = "data/raw/lokerid"):
        self.data_dir = Path(data_dir)
        self.engine = engine
        self.stats = {
            'total_rows': 0,
            'successful': 0,
            'failed': 0,
            'duplicates': 0,
            'files_processed': 0
        }
    
    def parse_salary(self, salary_text):
        """
        Extract salary min and max from text
        Examples:
        - "Rp 5.000.000 - Rp 8.000.000"
        - "5 juta - 8 juta"
        - "Negotiable"
        """
        if not salary_text or pd.isna(salary_text):
            return None, None, 'IDR'
        
        salary_text = str(salary_text).strip()
        
        # Pattern untuk angka dengan pemisah titik/koma
        pattern = r'(\d+(?:[.,]\d+)*)'
        matches = re.findall(pattern, salary_text)
        
        if not matches:
            return None, None, 'IDR'
        
        # Clean numbers (hapus pemisah)
        numbers = []
        for match in matches:
            cleaned = match.replace('.', '').replace(',', '')
            try:
                numbers.append(float(cleaned))
            except ValueError:
                continue
        
        if not numbers:
            return None, None, 'IDR'
        
        # Jika ada kata "juta" atau "million", multiply by 1,000,000
        if 'juta' in salary_text.lower() or 'million' in salary_text.lower():
            numbers = [n * 1_000_000 if n < 1000 else n for n in numbers]
        
        # Jika ada kata "ribu" atau "thousand", multiply by 1,000
        if 'ribu' in salary_text.lower() or 'thousand' in salary_text.lower():
            numbers = [n * 1_000 if n < 100 else n for n in numbers]
        
        # Get min and max
        salary_min = min(numbers) if numbers else None
        salary_max = max(numbers) if len(numbers) > 1 else salary_min
        
        return salary_min, salary_max, 'IDR'
    
    def parse_date(self, date_text):
        """Parse tanggal_posting ke format DATE"""
        if not date_text or pd.isna(date_text):
            return None
        
        # Jika sudah datetime
        if isinstance(date_text, datetime):
            return date_text.date()
        
        # Coba parse string
        try:
            # Format: YYYY-MM-DD atau DD/MM/YYYY
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(str(date_text), fmt).date()
                except ValueError:
                    continue
        except:
            pass
        
        return None
    
    def parse_scraping_time(self, time_text):
        """Parse waktu_scraping ke format DATETIME"""
        if not time_text or pd.isna(time_text):
            return None
        
        # Jika sudah datetime
        if isinstance(time_text, datetime):
            return time_text
        
        # Coba parse string
        try:
            # Format: YYYY-MM-DD HH:MM:SS
            for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    return datetime.strptime(str(time_text), fmt)
                except ValueError:
                    continue
        except:
            pass
        
        return None
    
    def clean_text(self, text):
        """Clean text data"""
        if pd.isna(text):
            return None
        
        text = str(text).strip()
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Keep most characters, just remove problematic ones
        # text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        
        return text if text else None
    
    def normalize_column_names(self, df):
        """Normalize column names to match database schema"""
        # Expected columns from CSV
        column_mapping = {
            'judul': 'judul',
            'perusahaan': 'perusahaan',
            'lokasi': 'lokasi',
            'lokasi_detail': 'lokasi_detail',
            'tipe_pekerjaan': 'tipe_pekerjaan',
            'level': 'level',
            'fungsi': 'fungsi',
            'pendidikan': 'pendidikan',
            'gaji': 'gaji',
            'industri': 'industri',
            'jumlah_karyawan': 'jumlah_karyawan',
            'tanggal_posting': 'tanggal_posting',
            'posting_relatif': 'posting_relatif',
            'waktu_scraping': 'waktu_scraping',
            'deskripsi_singkat': 'deskripsi_singkat',
            'tanggung_jawab': 'tanggung_jawab',
            'kualifikasi': 'kualifikasi',
            'keahlian': 'keahlian',
            'benefit': 'benefit',
            'url': 'url'
        }
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        
        return df
    
    def process_dataframe(self, df, source_file):
        """Process DataFrame: clean, parse, transform"""
        print_info(f"Processing {len(df)} rows from {source_file}")
        
        # Normalize column names
        df = self.normalize_column_names(df)
        
        # Add source column
        df['source'] = source_file
        
        # Clean text columns
        text_columns = [
            'judul', 'perusahaan', 'lokasi', 'lokasi_detail',
            'tipe_pekerjaan', 'level', 'fungsi', 'pendidikan',
            'industri', 'jumlah_karyawan', 'posting_relatif',
            'deskripsi_singkat', 'tanggung_jawab', 'kualifikasi',
            'keahlian', 'benefit'
        ]
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(self.clean_text)
        
        # Parse salary
        print_info("Parsing salary data...")
        if 'gaji' in df.columns:
            salary_data = df['gaji'].apply(self.parse_salary)
            df['gaji_min'] = salary_data.apply(lambda x: x[0])
            df['gaji_max'] = salary_data.apply(lambda x: x[1])
            df['gaji_currency'] = salary_data.apply(lambda x: x[2])
        else:
            df['gaji_min'] = None
            df['gaji_max'] = None
            df['gaji_currency'] = 'IDR'
        
        # Parse dates
        print_info("Parsing dates...")
        if 'tanggal_posting' in df.columns:
            df['tanggal_posting'] = df['tanggal_posting'].apply(self.parse_date)
        
        if 'waktu_scraping' in df.columns:
            df['waktu_scraping'] = df['waktu_scraping'].apply(self.parse_scraping_time)
        
        # Add processing flags
        df['is_processed'] = False
        df['is_annotated'] = False
        
        # Add timestamps
        now = datetime.now()
        df['created_at'] = now
        df['updated_at'] = now
        
        return df
    
    def check_duplicates(self, df, db: Session):
        """Check for duplicates based on URL"""
        
        # ========================================================================
        # DEDUPLICATION DISABLED - WILL IMPORT ALL ROWS
        # ========================================================================
        # Uncomment code below to enable deduplication by URL
        # ========================================================================
        
        print_info("Deduplication is DISABLED - importing all rows")
        return df
        
        # ========================================================================
        # ORIGINAL DEDUPLICATION CODE (COMMENTED OUT)
        # ========================================================================
        # Uncomment from here to enable deduplication:
        
        # if 'url' not in df.columns:
        #     return df
        # 
        # # Get existing URLs from database
        # existing_urls = set()
        # try:
        #     result = db.execute(text("SELECT url FROM jobs WHERE url IS NOT NULL"))
        #     existing_urls = {row[0] for row in result}
        # except Exception as e:
        #     print_warning(f"Could not check existing URLs: {e}")
        # 
        # # Filter out duplicates
        # if existing_urls:
        #     initial_count = len(df)
        #     df = df[~df['url'].isin(existing_urls)]
        #     duplicates = initial_count - len(df)
        #     
        #     if duplicates > 0:
        #         print_warning(f"Filtered out {duplicates} duplicate URLs")
        #         self.stats['duplicates'] += duplicates
        # 
        # return df
    
    def insert_to_database(self, df, db: Session, batch_size=100):
        """Insert DataFrame to database in batches"""
        total_rows = len(df)
        
        if total_rows == 0:
            print_warning("No data to insert")
            return
        
        print_info(f"Inserting {total_rows} rows in batches of {batch_size}...")
        
        # Insert in batches
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            try:
                # Convert to dict records
                records = batch.to_dict('records')
                
                # Build INSERT query
                columns = list(records[0].keys())
                placeholders = ', '.join([f':{col}' for col in columns])
                columns_str = ', '.join(columns)
                
                query = text(f"""
                    INSERT INTO jobs ({columns_str})
                    VALUES ({placeholders})
                """)
                
                # Execute batch
                for record in records:
                    # Convert None to NULL-compatible values
                    cleaned_record = {
                        k: (None if pd.isna(v) else v) 
                        for k, v in record.items()
                    }
                    db.execute(query, cleaned_record)
                
                db.commit()
                self.stats['successful'] += len(records)
                
                # Progress indicator
                progress = min(i + batch_size, total_rows)
                print(f"  Progress: {progress}/{total_rows} rows", end='\r')
                
            except Exception as e:
                db.rollback()
                print_error(f"\nBatch {i//batch_size + 1} failed: {e}")
                self.stats['failed'] += len(batch)
        
        print()  # New line after progress
        print_success(f"Inserted {self.stats['successful']} rows")
    
    def process_file(self, file_path: Path, db: Session):
        """Process single CSV file"""
        print_header(f"Processing: {file_path.name}")
        
        try:
            # Read CSV
            print_info("Reading CSV file...")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    print_info(f"Successfully read with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Could not read CSV with any encoding")
            
            initial_rows = len(df)
            self.stats['total_rows'] += initial_rows
            print_info(f"Read {initial_rows} rows")
            
            # Process DataFrame
            df = self.process_dataframe(df, file_path.name)
            
            # Check duplicates
            df = self.check_duplicates(df, db)
            
            # Insert to database
            if len(df) > 0:
                self.insert_to_database(df, db)
            else:
                print_warning("All rows were duplicates, nothing to insert")
            
            self.stats['files_processed'] += 1
            print_success(f"File {file_path.name} processed successfully")
            
        except Exception as e:
            print_error(f"Failed to process {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run migration for all CSV files"""
        print_header("CSV to MySQL Migration")
        print_info(f"Data directory: {self.data_dir}")
        
        # Check if directory exists
        if not self.data_dir.exists():
            print_error(f"Directory not found: {self.data_dir}")
            print_info("Creating directory...")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            print_success(f"Created {self.data_dir}")
            print()
            print_info("Please place your CSV files in this directory:")
            print(f"  {self.data_dir.absolute()}")
            return
        
        # Find CSV files
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            print_error(f"No CSV files found in {self.data_dir}")
            print()
            print_info("Expected files:")
            print("  - loker_data_*.csv")
            print()
            print_info("Place your CSV files in:")
            print(f"  {self.data_dir.absolute()}")
            return
        
        print_info(f"Found {len(csv_files)} CSV file(s)")
        for f in csv_files:
            print(f"  - {f.name}")
        
        # Confirm
        print()
        response = input(f"{Colors.WARNING}Proceed with migration? (yes/no): {Colors.ENDC}")
        if response.lower() not in ['yes', 'y']:
            print_info("Migration cancelled")
            return
        
        # Process each file
        db = SessionLocal()
        try:
            for csv_file in csv_files:
                self.process_file(csv_file, db)
        finally:
            db.close()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print migration summary"""
        print_header("Migration Summary")
        
        print(f"Files Processed:  {Colors.OKGREEN}{self.stats['files_processed']}{Colors.ENDC}")
        print(f"Total Rows:       {Colors.OKCYAN}{self.stats['total_rows']}{Colors.ENDC}")
        print(f"Successful:       {Colors.OKGREEN}{self.stats['successful']}{Colors.ENDC}")
        print(f"Duplicates:       {Colors.WARNING}{self.stats['duplicates']}{Colors.ENDC}")
        print(f"Failed:           {Colors.FAIL}{self.stats['failed']}{Colors.ENDC}")
        
        print()
        
        if self.stats['successful'] > 0:
            print_success("Migration completed successfully!")
            print()
            print("Next steps:")
            print("  1. Verify data: python scripts/verify_migration.py")
            print("  2. Check statistics: python scripts/data_statistics.py")
            print("  3. Start tokenization: python scripts/batch_tokenize.py")
        else:
            print_warning("No data was migrated. Check errors above.")


def main():
    """Main execution"""
    # Check if data directory exists
    data_dir = Path("data/raw/lokerid")
    
    # Run migration
    migrator = CSVMigrator(data_dir=str(data_dir))
    migrator.run()


if __name__ == "__main__":
    main()