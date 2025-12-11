"""
Script untuk membuat database tables
Run: python create_job_listings_table.py
"""

from app.database.base import Base
from app.database.session import engine

# Import semua models
from app.models.job_listing import JobListing

print("=" * 60)
print("Creating Job Listings Database Table")
print("=" * 60)
print()

print("Creating tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
    print()
    
    # Show created tables
    print("Created tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
        
        # Show columns for job_listings table
        if table.name == 'job_listings':
            print(f"    Columns ({len(table.columns)}):")
            for col in table.columns:
                print(f"      • {col.name}: {col.type}")
    
    print()
    print("=" * 60)
    print("✓ Database setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. python import_csv_data.py")
    print("  2. uvicorn app.main:app --reload")
    print()
    
except Exception as e:
    print(f"✗ Error creating tables: {e}")
    print()
