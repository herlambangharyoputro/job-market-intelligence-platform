"""
Script untuk menjalankan dan memverifikasi database migrations
Run: python run_migrations.py
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

def check_mysql_connection():
    """Check if MySQL is accessible"""
    print_header("Checking MySQL Connection")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print_error("DATABASE_URL not found in .env file")
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION()"))
            version = result.scalar()
            print_success(f"Connected to MySQL {version}")
            print_info(f"Database URL: {database_url.split('@')[1]}")
            return True
    except Exception as e:
        print_error(f"Failed to connect to MySQL: {e}")
        return False

def check_alembic_setup():
    """Check if Alembic is properly set up"""
    print_header("Checking Alembic Setup")
    
    # Check alembic.ini
    if os.path.exists("alembic.ini"):
        print_success("alembic.ini found")
    else:
        print_error("alembic.ini not found")
        return False
    
    # Check alembic directory
    if os.path.exists("alembic"):
        print_success("alembic/ directory found")
    else:
        print_error("alembic/ directory not found")
        return False
    
    # Check env.py
    if os.path.exists("alembic/env.py"):
        print_success("alembic/env.py found")
    else:
        print_error("alembic/env.py not found")
        return False
    
    # Check versions directory
    versions_dir = Path("alembic/versions")
    if versions_dir.exists():
        migration_files = list(versions_dir.glob("*.py"))
        if migration_files:
            print_success(f"Found {len(migration_files)} migration files")
            for mig in sorted(migration_files)[:5]:  # Show first 5
                print_info(f"  - {mig.name}")
            if len(migration_files) > 5:
                print_info(f"  ... and {len(migration_files) - 5} more")
        else:
            print_warning("No migration files found in alembic/versions/")
    else:
        print_error("alembic/versions/ directory not found")
        return False
    
    return True

def run_migrations():
    """Run Alembic migrations"""
    print_header("Running Migrations")
    
    print_info("Executing: alembic upgrade head")
    result = os.system("alembic upgrade head")
    
    if result == 0:
        print_success("Migrations completed successfully!")
        return True
    else:
        print_error("Migrations failed!")
        return False

def verify_tables():
    """Verify that all tables were created"""
    print_header("Verifying Tables")
    
    expected_tables = [
        'jobs',
        'annotation_types',
        'annotations',
        'annotation_labels',
        'annotation_rules',
        'annotation_history',
        'annotators',
        'annotation_tasks',
        'annotation_quality',
        'skills_taxonomy',
        'location_mappings',
        'company_profiles',
        'salary_ranges',
        'job_categories',
        'benefit_categories',
        'alembic_version'  # Alembic metadata table
    ]
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    existing_tables = inspector.get_table_names()
    
    print_info(f"Found {len(existing_tables)} tables in database")
    print()
    
    all_present = True
    for table in expected_tables:
        if table in existing_tables:
            print_success(f"{table}")
        else:
            print_error(f"{table} - MISSING!")
            all_present = False
    
    if all_present:
        print()
        print_success("All expected tables are present!")
    else:
        print()
        print_warning("Some tables are missing. Check migration logs.")
    
    return all_present

def show_table_info():
    """Show basic info about created tables"""
    print_header("Table Information")
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    
    # Count rows in key tables
    tables_to_check = ['jobs', 'annotations', 'annotation_types']
    
    with engine.connect() as connection:
        for table in tables_to_check:
            try:
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print_info(f"{table}: {count} rows")
            except Exception as e:
                print_warning(f"{table}: Unable to count ({str(e)[:50]}...)")

def show_migration_status():
    """Show current Alembic migration status"""
    print_header("Migration Status")
    
    print_info("Executing: alembic current")
    os.system("alembic current")
    print()
    
    print_info("Executing: alembic history")
    os.system("alembic history")

def main():
    """Main execution"""
    print_header("Database Migration Tool")
    print_info("Job Market Intelligence Platform - Annotation System")
    print()
    
    # Step 1: Check MySQL connection
    if not check_mysql_connection():
        print_error("Cannot proceed without MySQL connection")
        sys.exit(1)
    
    # Step 2: Check Alembic setup
    if not check_alembic_setup():
        print_error("Alembic is not properly set up")
        sys.exit(1)
    
    # Step 3: Ask user confirmation
    print()
    response = input(f"{Colors.WARNING}Do you want to run migrations now? (yes/no): {Colors.ENDC}")
    if response.lower() not in ['yes', 'y']:
        print_info("Migration cancelled by user")
        sys.exit(0)
    
    # Step 4: Run migrations
    if not run_migrations():
        print_error("Migration failed. Check the errors above.")
        sys.exit(1)
    
    # Step 5: Verify tables
    verify_tables()
    
    # Step 6: Show table info
    show_table_info()
    
    # Step 7: Show migration status
    show_migration_status()
    
    # Final summary
    print_header("Migration Complete!")
    print_success("Database schema has been created successfully")
    print()
    print_info("Next steps:")
    print("  1. Run seed data script to populate initial data")
    print("  2. Migrate XLSX data to MySQL")
    print("  3. Setup tokenization services")
    print("  4. Test annotation API endpoints")
    print()

if __name__ == "__main__":
    main()
