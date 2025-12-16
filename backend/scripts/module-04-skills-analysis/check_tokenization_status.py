# Location: backend/scripts/module-04-skills-analysis/check_tokenization_status.py
"""
Diagnostic Script - Check Tokenization Status
Module #4: Skills Demand Analysis - Diagnostic Tool

Checks database for tokenized jobs and token structure format
to troubleshoot "No tokenized jobs found" error

Run: python scripts/module-04-skills-analysis/check_tokenization_status.py

Author: Arya
Date: 2025-12-16
Project: Job Market Intelligence Platform
"""

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@localhost:3306/job_market_intelligence_platform'
)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def check_database():
    """Check database for tokenized jobs and structure"""
    
    print_header("TOKENIZATION STATUS DIAGNOSTIC")
    print_info(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # 1. Check total jobs
            print("\n" + "📊 BASIC STATISTICS".center(70))
            print("-" * 70)
            
            result = conn.execute(text("SELECT COUNT(*) as total FROM jobs"))
            total_jobs = result.scalar()
            print(f"Total jobs in database:          {total_jobs:,}")
            
            # 2. Check tokenized jobs
            result = conn.execute(text("SELECT COUNT(*) as total FROM jobs WHERE is_tokenized = TRUE"))
            tokenized_jobs = result.scalar()
            print(f"Jobs with is_tokenized=TRUE:     {tokenized_jobs:,}")
            
            # 3. Check jobs with tokens column populated
            result = conn.execute(text("SELECT COUNT(*) as total FROM jobs WHERE tokens IS NOT NULL"))
            jobs_with_tokens = result.scalar()
            print(f"Jobs with tokens != NULL:        {jobs_with_tokens:,}")
            
            # 4. Check both conditions
            result = conn.execute(text("""
                SELECT COUNT(*) as total 
                FROM jobs 
                WHERE is_tokenized = TRUE 
                AND tokens IS NOT NULL
            """))
            fully_tokenized = result.scalar()
            print(f"Jobs with BOTH conditions:       {fully_tokenized:,}")
            
            if fully_tokenized > 0:
                percentage = (fully_tokenized / total_jobs * 100) if total_jobs > 0 else 0
                print(f"Tokenization completion:         {percentage:.1f}%")
            
            # 5. Sample token structure
            if jobs_with_tokens > 0:
                print("\n" + "📝 SAMPLE TOKEN STRUCTURE".center(70))
                print("-" * 70)
                
                result = conn.execute(text("""
                    SELECT id, judul, tokens, is_tokenized
                    FROM jobs 
                    WHERE tokens IS NOT NULL
                    LIMIT 3
                """))
                
                samples = list(result)
                
                for i, row in enumerate(samples, 1):
                    print(f"\n{Colors.BOLD}--- Sample {i} of {len(samples)} ---{Colors.ENDC}")
                    print(f"Job ID:        {row[0]}")
                    print(f"Title:         {row[1][:60]}...")
                    print(f"is_tokenized:  {row[3]}")
                    
                    try:
                        # Parse tokens
                        if isinstance(row[2], str):
                            tokens = json.loads(row[2])
                        else:
                            tokens = row[2]
                        
                        # Print top-level keys
                        print(f"\nToken keys:    {list(tokens.keys())}")
                        
                        # Analyze skills structure
                        if 'skills' in tokens:
                            skills_data = tokens['skills']
                            print(f"\n{Colors.OKCYAN}Skills data found!{Colors.ENDC}")
                            print(f"  Type:        {type(skills_data).__name__}")
                            
                            if isinstance(skills_data, dict):
                                print(f"  Keys:        {list(skills_data.keys())}")
                                
                                # Check nested skills
                                if 'skills' in skills_data:
                                    skill_list = skills_data['skills']
                                    if isinstance(skill_list, list) and len(skill_list) > 0:
                                        print(f"  Count:       {len(skill_list)} skills")
                                        print(f"  Sample:      {skill_list[0]}")
                                        print_success("Skills format: LIST of skills ✓")
                                    else:
                                        print_warning("Skills list is empty or invalid")
                                
                                # Check categorized
                                if 'categorized' in skills_data:
                                    categorized = skills_data['categorized']
                                    if isinstance(categorized, dict):
                                        categories = list(categorized.keys())
                                        print(f"  Categories:  {', '.join(categories[:5])}")
                                        
                                        # Sample first category
                                        if categories:
                                            first_cat = categories[0]
                                            first_skills = categorized[first_cat]
                                            print(f"  {first_cat}: {first_skills[:3] if isinstance(first_skills, list) else first_skills}")
                                        
                                        print_success("Categorized format: DICT by category ✓")
                            
                            elif isinstance(skills_data, list):
                                print(f"  Count:       {len(skills_data)} skills")
                                if skills_data:
                                    print(f"  Sample:      {skills_data[0]}")
                                print_success("Skills format: FLAT LIST ✓")
                        
                        else:
                            print_error("No 'skills' key found in tokens!")
                            print(f"Available keys: {list(tokens.keys())}")
                        
                        # Show structure preview
                        print(f"\n{Colors.BOLD}Token structure (first 400 chars):{Colors.ENDC}")
                        tokens_str = json.dumps(tokens, indent=2, ensure_ascii=False)[:400]
                        print(tokens_str + "...")
                    
                    except Exception as e:
                        print_error(f"Error parsing tokens: {e}")
                        print(f"Raw tokens type: {type(row[2])}")
            
            else:
                print_error("No jobs with tokens found in database!")
            
            # 6. Recommendations
            print_header("💡 RECOMMENDATIONS & NEXT STEPS")
            
            if fully_tokenized == 0:
                print_error("No tokenized jobs found!")
                print("\nNext steps:")
                print("  1. Check tokenization scripts location")
                print("  2. Run tokenization on jobs data")
                print("  3. Verify data after tokenization")
                print()
            
            elif fully_tokenized > 0:
                print_success(f"{fully_tokenized:,} jobs tokenized successfully!")
                print("\nToken structure looks good. Analytics service should work.")
                print()
    
    except Exception as e:
        print_error(f"Database error: {e}")
        return False
    
    print("=" * 70)
    return True


if __name__ == "__main__":
    print()
    check_database()
    print()