# Location: backend/scripts/module-05-validation/seed_skill_categories.py
"""
Seed Initial Skill Categories
Module #5: Skill Validation System

Populates skill_categories table with initial taxonomy

Run: python scripts/module-05-validation/seed_skill_categories.py

Author: Arya
Date: 2025-12-16
"""

import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@localhost:3306/job_market_intelligence_platform'
)


def seed_categories():
    """Seed initial skill categories"""
    
    print("\n" + "=" * 70)
    print("SEED SKILL CATEGORIES - MODULE #5")
    print("=" * 70)
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Initial categories with metadata
        categories = [
            # Programming & Development
            {
                'category_name': 'programming_language',
                'display_name': 'Programming Languages',
                'description': 'Programming languages like Python, Java, JavaScript',
                'icon': '💻',
                'color': '#3B82F6',
                'sort_order': 1
            },
            {
                'category_name': 'frontend',
                'display_name': 'Frontend Development',
                'description': 'Frontend frameworks and libraries (React, Vue, Angular)',
                'icon': '🎨',
                'color': '#10B981',
                'sort_order': 2
            },
            {
                'category_name': 'backend',
                'display_name': 'Backend Development',
                'description': 'Backend frameworks (Django, Flask, Spring, Node.js)',
                'icon': '⚙️',
                'color': '#8B5CF6',
                'sort_order': 3
            },
            {
                'category_name': 'mobile',
                'display_name': 'Mobile Development',
                'description': 'Mobile platforms and frameworks (iOS, Android, React Native)',
                'icon': '📱',
                'color': '#F59E0B',
                'sort_order': 4
            },
            
            # Data & Infrastructure
            {
                'category_name': 'database',
                'display_name': 'Databases',
                'description': 'Database systems (MySQL, PostgreSQL, MongoDB, Redis)',
                'icon': '🗄️',
                'color': '#EF4444',
                'sort_order': 5
            },
            {
                'category_name': 'devops',
                'display_name': 'DevOps & Infrastructure',
                'description': 'DevOps tools (Docker, Kubernetes, CI/CD, Jenkins)',
                'icon': '🔧',
                'color': '#06B6D4',
                'sort_order': 6
            },
            {
                'category_name': 'cloud',
                'display_name': 'Cloud Platforms',
                'description': 'Cloud services (AWS, Azure, GCP, Heroku)',
                'icon': '☁️',
                'color': '#0EA5E9',
                'sort_order': 7
            },
            
            # Specialized Tech
            {
                'category_name': 'ai_ml',
                'display_name': 'AI & Machine Learning',
                'description': 'ML frameworks (TensorFlow, PyTorch, Scikit-learn)',
                'icon': '🤖',
                'color': '#EC4899',
                'sort_order': 8
            },
            {
                'category_name': 'data_science',
                'display_name': 'Data Science & Analytics',
                'description': 'Data tools (Pandas, NumPy, Tableau, Power BI)',
                'icon': '📊',
                'color': '#14B8A6',
                'sort_order': 9
            },
            
            # Design & Tools
            {
                'category_name': 'design_tools',
                'display_name': 'Design Tools',
                'description': 'Design software (Figma, Adobe XD, Photoshop, Illustrator)',
                'icon': '🎨',
                'color': '#F97316',
                'sort_order': 10
            },
            {
                'category_name': 'productivity_tools',
                'display_name': 'Productivity Tools',
                'description': 'Office and productivity software (Excel, Word, Notion)',
                'icon': '📝',
                'color': '#84CC16',
                'sort_order': 11
            },
            
            # Business & Marketing
            {
                'category_name': 'marketing',
                'display_name': 'Digital Marketing',
                'description': 'Marketing skills (SEO, SEM, Content Marketing, Social Media)',
                'icon': '📢',
                'color': '#A855F7',
                'sort_order': 12
            },
            {
                'category_name': 'sales',
                'display_name': 'Sales & Business Development',
                'description': 'Sales and business skills',
                'icon': '💼',
                'color': '#22C55E',
                'sort_order': 13
            },
            {
                'category_name': 'finance',
                'display_name': 'Finance & Accounting',
                'description': 'Financial and accounting skills',
                'icon': '💰',
                'color': '#EAB308',
                'sort_order': 14
            },
            
            # Soft Skills
            {
                'category_name': 'soft_skills',
                'display_name': 'Soft Skills',
                'description': 'Interpersonal skills (Communication, Leadership, Teamwork)',
                'icon': '🤝',
                'color': '#6366F1',
                'sort_order': 15
            },
            {
                'category_name': 'languages',
                'display_name': 'Languages',
                'description': 'Spoken languages (English, Mandarin, etc)',
                'icon': '🌐',
                'color': '#14B8A6',
                'sort_order': 16
            },
            
            # Domain Specific
            {
                'category_name': 'domain_knowledge',
                'display_name': 'Domain Knowledge',
                'description': 'Industry-specific knowledge and expertise',
                'icon': '📚',
                'color': '#64748B',
                'sort_order': 17
            },
            
            # Methodologies
            {
                'category_name': 'methodologies',
                'display_name': 'Methodologies & Frameworks',
                'description': 'Work methodologies (Agile, Scrum, Lean, Six Sigma)',
                'icon': '📋',
                'color': '#78716C',
                'sort_order': 18
            },
            
            # Certifications
            {
                'category_name': 'certifications',
                'display_name': 'Certifications',
                'description': 'Professional certifications',
                'icon': '🎓',
                'color': '#D97706',
                'sort_order': 19
            },
            
            # Uncategorized
            {
                'category_name': 'uncategorized',
                'display_name': 'Uncategorized',
                'description': 'Skills not yet categorized',
                'icon': '❓',
                'color': '#9CA3AF',
                'sort_order': 99
            },
        ]
        
        print(f"\n📥 Inserting {len(categories)} categories...")
        
        inserted = 0
        skipped = 0
        
        for cat in categories:
            # Check if exists
            result = db.execute(
                text("SELECT id FROM skill_categories WHERE category_name = :name"),
                {'name': cat['category_name']}
            )
            
            if result.fetchone():
                print(f"   ⏭️  Skip: {cat['category_name']} (already exists)")
                skipped += 1
                continue
            
            # Insert
            db.execute(
                text("""
                    INSERT INTO skill_categories 
                    (category_name, display_name, description, icon, color, sort_order, is_active)
                    VALUES 
                    (:category_name, :display_name, :description, :icon, :color, :sort_order, TRUE)
                """),
                cat
            )
            
            print(f"   ✅ {cat['icon']} {cat['display_name']}")
            inserted += 1
        
        db.commit()
        
        # Verify
        result = db.execute(text("SELECT COUNT(*) FROM skill_categories"))
        total = result.scalar()
        
        print("\n" + "=" * 70)
        print("✅ SEED COMPLETE")
        print("=" * 70)
        print(f"\nResults:")
        print(f"   • Inserted: {inserted}")
        print(f"   • Skipped: {skipped}")
        print(f"   • Total in DB: {total}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Populate validation queue from job data")
        print(f"   2. Start validation interface")
        print(f"   3. Begin supervised curation")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()