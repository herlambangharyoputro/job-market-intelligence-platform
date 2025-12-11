"""
Script untuk membuat database tables
Run: python create_tables.py
"""

from app.database.base import Base
from app.database.session import engine

# Import semua models agar Base.metadata mengenali mereka
from app.models.job import Job

print("=" * 60)
print("Creating Database Tables")
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
    
    print()
    print("=" * 60)
    print("✓ Database setup complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Error creating tables: {e}")
    print()