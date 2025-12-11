"""
Script untuk seed data awal annotation system
Run: python seed_initial_data.py
"""

import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.job import Job
from datetime import datetime

def seed_annotation_types(db: Session):
    """Seed initial annotation types"""
    print("\n" + "=" * 60)
    print("Seeding Annotation Types")
    print("=" * 60)
    
    from sqlalchemy import text
    
    annotation_types = [
        {
            'code': 'NER',
            'name': 'Named Entity Recognition',
            'description': 'Extract named entities like companies, locations, technologies',
            'category': 'NLP',
            'entity_field': None,
            'allows_multiple': True,
            'requires_validation': False,
            'color_code': '#3B82F6'
        },
        {
            'code': 'SKILL_EXTRACTION',
            'name': 'Skill Extraction',
            'description': 'Extract technical and soft skills from job descriptions',
            'category': 'Extraction',
            'entity_field': 'keahlian',
            'allows_multiple': True,
            'requires_validation': False,
            'color_code': '#10B981'
        },
        {
            'code': 'SENTIMENT',
            'name': 'Sentiment Analysis',
            'description': 'Analyze sentiment/tone of job description',
            'category': 'NLP',
            'entity_field': 'deskripsi_singkat',
            'allows_multiple': False,
            'requires_validation': True,
            'color_code': '#F59E0B'
        },
        {
            'code': 'JOB_CLASSIFICATION',
            'name': 'Job Classification',
            'description': 'Classify job into categories and subcategories',
            'category': 'Classification',
            'entity_field': 'judul',
            'allows_multiple': False,
            'requires_validation': True,
            'color_code': '#8B5CF6'
        },
        {
            'code': 'REQUIREMENT_EXTRACTION',
            'name': 'Requirement Extraction',
            'description': 'Extract job requirements (education, experience, etc)',
            'category': 'Extraction',
            'entity_field': 'kualifikasi',
            'allows_multiple': True,
            'requires_validation': False,
            'color_code': '#EF4444'
        },
        {
            'code': 'BENEFIT_EXTRACTION',
            'name': 'Benefit Extraction',
            'description': 'Extract and categorize job benefits',
            'category': 'Extraction',
            'entity_field': 'benefit',
            'allows_multiple': True,
            'requires_validation': False,
            'color_code': '#06B6D4'
        },
        {
            'code': 'SALARY_PARSING',
            'name': 'Salary Parsing',
            'description': 'Extract and parse salary information',
            'category': 'Extraction',
            'entity_field': 'gaji',
            'allows_multiple': False,
            'requires_validation': True,
            'color_code': '#84CC16'
        },
        {
            'code': 'LOCATION_NER',
            'name': 'Location NER',
            'description': 'Extract and normalize location information',
            'category': 'NLP',
            'entity_field': 'lokasi',
            'allows_multiple': True,
            'requires_validation': False,
            'color_code': '#EC4899'
        }
    ]
    
    inserted = 0
    for i, at in enumerate(annotation_types, 1):
        try:
            query = text("""
                INSERT INTO annotation_types 
                (code, name, description, category, entity_field, allows_multiple, 
                 requires_validation, display_order, color_code)
                VALUES 
                (:code, :name, :description, :category, :entity_field, :allows_multiple,
                 :requires_validation, :display_order, :color_code)
            """)
            
            db.execute(query, {
                **at,
                'display_order': i
            })
            db.commit()
            print(f"✓ Inserted: {at['name']}")
            inserted += 1
        except Exception as e:
            print(f"✗ Failed to insert {at['name']}: {e}")
            db.rollback()
    
    print(f"\n✓ Seeded {inserted}/{len(annotation_types)} annotation types")
    return inserted

def seed_annotation_labels(db: Session):
    """Seed initial annotation labels"""
    print("\n" + "=" * 60)
    print("Seeding Annotation Labels")
    print("=" * 60)
    
    from sqlalchemy import text
    
    # Get annotation_type_id for SKILL_EXTRACTION
    result = db.execute(text("SELECT id FROM annotation_types WHERE code = 'SKILL_EXTRACTION'")).first()
    if not result:
        print("✗ SKILL_EXTRACTION type not found, skipping labels")
        return 0
    
    skill_type_id = result[0]
    
    skill_labels = [
        ('SKILL_PYTHON', 'Python', 'Programming language Python'),
        ('SKILL_JAVA', 'Java', 'Programming language Java'),
        ('SKILL_JAVASCRIPT', 'JavaScript', 'Programming language JavaScript'),
        ('SKILL_SQL', 'SQL', 'Database query language'),
        ('SKILL_REACT', 'React', 'Frontend framework React'),
        ('SKILL_DJANGO', 'Django', 'Python web framework'),
        ('SKILL_COMMUNICATION', 'Communication', 'Soft skill: Communication'),
        ('SKILL_TEAMWORK', 'Teamwork', 'Soft skill: Teamwork'),
        ('SKILL_PROBLEM_SOLVING', 'Problem Solving', 'Soft skill: Problem solving'),
        ('SKILL_LEADERSHIP', 'Leadership', 'Soft skill: Leadership')
    ]
    
    inserted = 0
    for i, (code, name, desc) in enumerate(skill_labels, 1):
        try:
            query = text("""
                INSERT INTO annotation_labels 
                (annotation_type_id, label_code, label_name, description, display_order)
                VALUES 
                (:type_id, :code, :name, :desc, :order)
            """)
            
            db.execute(query, {
                'type_id': skill_type_id,
                'code': code,
                'name': name,
                'desc': desc,
                'order': i
            })
            db.commit()
            print(f"✓ Inserted: {name}")
            inserted += 1
        except Exception as e:
            print(f"✗ Failed to insert {name}: {e}")
            db.rollback()
    
    print(f"\n✓ Seeded {inserted}/{len(skill_labels)} annotation labels")
    return inserted

def seed_annotators(db: Session):
    """Seed initial annotators"""
    print("\n" + "=" * 60)
    print("Seeding Annotators")
    print("=" * 60)
    
    from sqlalchemy import text
    
    annotators = [
        {
            'username': 'system',
            'full_name': 'System Auto-Annotator',
            'annotator_type': 'ai_model',
            'role': 'system',
            'can_validate': False,
            'can_create_labels': False
        },
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'full_name': 'Admin User',
            'annotator_type': 'human',
            'role': 'admin',
            'can_validate': True,
            'can_create_labels': True
        },
        {
            'username': 'annotator1',
            'email': 'annotator1@example.com',
            'full_name': 'Annotator 1',
            'annotator_type': 'human',
            'role': 'annotator',
            'can_validate': False,
            'can_create_labels': False
        }
    ]
    
    inserted = 0
    for ann in annotators:
        try:
            query = text("""
                INSERT INTO annotators 
                (username, email, full_name, annotator_type, role, 
                 can_validate, can_create_labels)
                VALUES 
                (:username, :email, :full_name, :annotator_type, :role,
                 :can_validate, :can_create_labels)
            """)
            
            db.execute(query, ann)
            db.commit()
            print(f"✓ Inserted: {ann['username']}")
            inserted += 1
        except Exception as e:
            print(f"✗ Failed to insert {ann['username']}: {e}")
            db.rollback()
    
    print(f"\n✓ Seeded {inserted}/{len(annotators)} annotators")
    return inserted

def verify_seeding(db: Session):
    """Verify seeded data"""
    print("\n" + "=" * 60)
    print("Verifying Seeded Data")
    print("=" * 60)
    
    from sqlalchemy import text
    
    tables = [
        ('annotation_types', 'Annotation Types'),
        ('annotation_labels', 'Annotation Labels'),
        ('annotators', 'Annotators')
    ]
    
    for table, name in tables:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"✓ {name}: {result} rows")
        except Exception as e:
            print(f"✗ {name}: Error - {e}")

def main():
    """Main execution"""
    print("=" * 60)
    print("Initial Data Seeding")
    print("Job Market Intelligence Platform - Annotation System")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed annotation types
        types_count = seed_annotation_types(db)
        
        # Seed annotation labels
        labels_count = seed_annotation_labels(db)
        
        # Seed annotators
        annotators_count = seed_annotators(db)
        
        # Verify
        verify_seeding(db)
        
        # Summary
        print("\n" + "=" * 60)
        print("Seeding Complete!")
        print("=" * 60)
        print(f"✓ Annotation Types: {types_count}")
        print(f"✓ Annotation Labels: {labels_count}")
        print(f"✓ Annotators: {annotators_count}")
        print("\nNext steps:")
        print("  1. Migrate XLSX data: python scripts/migrate_xlsx_to_mysql.py")
        print("  2. Start tokenization: python scripts/batch_tokenize.py")
        print("  3. Run auto-annotation: python scripts/auto_annotate.py")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
