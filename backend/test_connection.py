from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✓ Database connection successful!")
        print(f"✓ Connected to: {DATABASE_URL.split('@')[1]}")
except Exception as e:
    print(f"✗ Database connection failed!")
    print(f"Error: {e}")