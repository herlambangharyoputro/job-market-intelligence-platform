"""
Script untuk seed data awal annotation system
Run: python scripts/database_schema/seed_initial_data.py
"""

import sys
import os
from pathlib import Path

# Add backend root to Python path
# Current file: backend/scripts/database_schema/seed_initial_data.py
# We need: backend/
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine
from datetime import datetime


# Colors for output
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def seed_annotation_types(db: Session):
    """Seed annotation types"""
    
    annotation_types = [
        {
            'code': 'NER',
            'name': 'Named Entity Recognition',
            'description': 'Extract named entities like companies, locations, technologies',
            'category': 'NLP',
            'color_code': '#3B82F6',
            'is_active': True
        },
        {
            'code': 'SKILL_EXTRACTION',
            'name': 'Skill Extraction',
            'description': 'Extract technical and soft skills from job descriptions',
            'category': 'Extraction',
            'color_code': '#10B981',
            'is_active': True
        },
        {
            'code': 'SENTIMENT',
            'name': 'Sentiment Analysis',
            'description': 'Analyze sentiment/tone of job descriptions',
            'category': 'NLP',
            'color_code': '#F59E0B',
            'is_active': True
        },
        {
            'code': 'JOB_CLASSIFICATION',
            'name': 'Job Classification',
            'description': 'Classify jobs into categories',
            'category': 'Classification',
            'color_code': '#8B5CF6',
            'is_active': True
        },
        {
            'code': 'REQUIREMENT_EXTRACTION',
            'name': 'Requirement Extraction',
            'description': 'Extract job requirements (education, experience, etc)',
            'category': 'Extraction',
            'color_code': '#EF4444',
            'is_active': True
        },
        {
            'code': 'BENEFIT_EXTRACTION',
            'name': 'Benefit Extraction',
            'description': 'Extract and categorize job benefits',
            'category': 'Extraction',
            'color_code': '#06B6D4',
            'is_active': True
        },
        {
            'code': 'SALARY_PARSING',
            'name': 'Salary Parsing',
            'description': 'Parse and extract salary information',
            'category': 'Extraction',
            'color_code': '#84CC16',
            'is_active': True
        },
        {
            'code': 'LOCATION_NER',
            'name': 'Location NER',
            'description': 'Extract and normalize location information',
            'category': 'NLP',
            'color_code': '#EC4899',
            'is_active': True
        }
    ]
    
    count = 0
    for at in annotation_types:
        try:
            # Check if exists
            result = db.execute(
                text("SELECT id FROM annotation_types WHERE code = :code"),
                {'code': at['code']}
            ).first()
            
            if result:
                print(f"  - {at['code']}: already exists, skipping")
                continue
            
            # Insert
            db.execute(
                text("""
                    INSERT INTO annotation_types 
                    (code, name, description, category, color_code, is_active, created_at, updated_at)
                    VALUES 
                    (:code, :name, :description, :category, :color_code, :is_active, NOW(), NOW())
                """),
                at
            )
            count += 1
            print(f"  ✓ {at['code']}: {at['name']}")
            
        except Exception as e:
            print(f"  ✗ Error inserting {at['code']}: {e}")
    
    db.commit()
    return count


def seed_annotation_labels(db: Session):
    """Seed annotation labels for skill extraction"""
    
    # Get SKILL_EXTRACTION type ID
    result = db.execute(
        text("SELECT id FROM annotation_types WHERE code = 'SKILL_EXTRACTION'")
    ).first()
    
    if not result:
        print("  ⚠ SKILL_EXTRACTION type not found, skipping labels")
        return 0
    
    type_id = result[0]
    
    labels = [
        # Programming languages
        ('SKILL_PYTHON', 'Python', 'Programming language Python'),
        ('SKILL_JAVA', 'Java', 'Programming language Java'),
        ('SKILL_JAVASCRIPT', 'JavaScript', 'Programming language JavaScript'),
        ('SKILL_SQL', 'SQL', 'Database query language'),
        ('SKILL_PHP', 'PHP', 'Programming language PHP'),
        
        # Frameworks
        ('SKILL_REACT', 'React', 'Frontend framework React'),
        ('SKILL_DJANGO', 'Django', 'Python web framework'),
        ('SKILL_LARAVEL', 'Laravel', 'PHP framework'),
        
        # Soft skills
        ('SKILL_COMMUNICATION', 'Communication', 'Communication skills'),
        ('SKILL_TEAMWORK', 'Teamwork', 'Ability to work in teams'),
        ('SKILL_PROBLEM_SOLVING', 'Problem Solving', 'Problem solving ability'),
        ('SKILL_LEADERSHIP', 'Leadership', 'Leadership skills'),
    ]
    
    count = 0
    for label_code, label_name, description in labels:
        try:
            # Check if exists
            result = db.execute(
                text("SELECT id FROM annotation_labels WHERE label_code = :code"),
                {'code': label_code}
            ).first()
            
            if result:
                continue
            
            # Insert
            db.execute(
                text("""
                    INSERT INTO annotation_labels 
                    (annotation_type_id, label_code, label_name, description, is_active, created_at, updated_at)
                    VALUES 
                    (:type_id, :label_code, :label_name, :description, TRUE, NOW(), NOW())
                """),
                {
                    'type_id': type_id,
                    'label_code': label_code,
                    'label_name': label_name,
                    'description': description
                }
            )
            count += 1
            print(f"  ✓ {label_code}: {label_name}")
            
        except Exception as e:
            print(f"  ✗ Error inserting {label_code}: {e}")
    
    db.commit()
    return count


def seed_annotators(db: Session):
    """Seed annotators"""
    
    annotators = [
        {
            'username': 'system',
            'email': 'system@jobmarket.ai',
            'annotator_type': 'ai_model',
            'role': 'system',
            'is_active': True
        },
        {
            'username': 'admin',
            'email': 'admin@jobmarket.ai',
            'annotator_type': 'human',
            'role': 'admin',
            'is_active': True,
            'can_validate': True,
            'can_create_labels': True
        },
        {
            'username': 'annotator1',
            'email': 'annotator1@jobmarket.ai',
            'annotator_type': 'human',
            'role': 'annotator',
            'is_active': True,
            'can_validate': False,
            'can_create_labels': False
        }
    ]
    
    count = 0
    for ann in annotators:
        try:
            # Check if exists
            result = db.execute(
                text("SELECT id FROM annotators WHERE username = :username"),
                {'username': ann['username']}
            ).first()
            
            if result:
                print(f"  - {ann['username']}: already exists, skipping")
                continue
            
            # Build INSERT query dynamically
            columns = ', '.join(ann.keys())
            placeholders = ', '.join([f':{k}' for k in ann.keys()])
            
            db.execute(
                text(f"""
                    INSERT INTO annotators 
                    ({columns}, created_at, updated_at)
                    VALUES 
                    ({placeholders}, NOW(), NOW())
                """),
                ann
            )
            count += 1
            print(f"  ✓ {ann['username']}: {ann['role']}")
            
        except Exception as e:
            print(f"  ✗ Error inserting {ann['username']}: {e}")
    
    db.commit()
    return count


def main():
    """Main seed function"""
    
    print_header("Seeding Initial Data")
    
    db = SessionLocal()
    
    try:
        # Seed annotation types
        print("1. Seeding annotation types...")
        count = seed_annotation_types(db)
        print_success(f"Seeded {count} annotation types")
        print()
        
        # Seed annotation labels
        print("2. Seeding annotation labels...")
        count = seed_annotation_labels(db)
        print_success(f"Seeded {count} annotation labels")
        print()
        
        # Seed annotators
        print("3. Seeding annotators...")
        count = seed_annotators(db)
        print_success(f"Seeded {count} annotators")
        print()
        
        print_header("Seed Completed Successfully!")
        
        # Show summary
        print("Summary:")
        result = db.execute(text("SELECT COUNT(*) FROM annotation_types")).scalar()
        print(f"  - Annotation types: {result}")
        
        result = db.execute(text("SELECT COUNT(*) FROM annotation_labels")).scalar()
        print(f"  - Annotation labels: {result}")
        
        result = db.execute(text("SELECT COUNT(*) FROM annotators")).scalar()
        print(f"  - Annotators: {result}")
        print()
        
    except Exception as e:
        print_error(f"Seed failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()