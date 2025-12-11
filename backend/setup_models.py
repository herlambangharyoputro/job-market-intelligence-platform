"""
Setup script untuk membuat models dan tables
Run: python setup_models.py
"""

import os

print("=" * 60)
print("Setting up Models and Database")
print("=" * 60)
print()

# 1. Create app/models/job.py
print("Creating app/models/job.py...")
job_model = '''from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database.base import Base
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    company = Column(String(255), index=True)
    location = Column(String(255))
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    job_type = Column(String(50))
    experience_level = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
'''

with open('app/models/job.py', 'w', encoding='utf-8') as f:
    f.write(job_model)
print("✓ Created app/models/job.py")

# 2. Update app/models/__init__.py
print("Updating app/models/__init__.py...")
models_init = '''from app.models.job import Job

__all__ = ["Job"]
'''

with open('app/models/__init__.py', 'w', encoding='utf-8') as f:
    f.write(models_init)
print("✓ Updated app/models/__init__.py")

# 3. Update app/database/__init__.py
print("Updating app/database/__init__.py...")
database_init = '''from app.database.base import Base
from app.database.session import engine, SessionLocal, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
'''

with open('app/database/__init__.py', 'w', encoding='utf-8') as f:
    f.write(database_init)
print("✓ Updated app/database/__init__.py")

# 4. Create create_tables.py
print("Creating create_tables.py...")
create_tables = '''"""
Script untuk membuat database tables
Run: python create_tables.py
"""

from app.database.base import Base
from app.database.session import engine

# Import semua models
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
'''

with open('create_tables.py', 'w', encoding='utf-8') as f:
    f.write(create_tables)
print("✓ Created create_tables.py")

print()
print("=" * 60)
print("✓ Setup Complete!")
print("=" * 60)
print()
print("Now run:")
print("  python create_tables.py")
print()