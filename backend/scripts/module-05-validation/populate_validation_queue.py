# Location: backend/scripts/module-05-validation/populate_validation_queue.py
"""
Populate Validation Queue
Module #5: Skill Validation System

Extracts skills from tokenized jobs and adds them to validation queue
Prioritizes by frequency (most common skills reviewed first)

Run: python scripts/module-05-validation/populate_validation_queue.py

Options:
  --limit N       Limit number of unique skills to add (default: 1000)
  --min-count N   Minimum occurrence count (default: 2)

Author: Arya
Date: 2025-12-16
"""

import sys
from pathlib import Path

backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

import os
import json
from collections import Counter
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:root@localhost:3306/job_market_intelligence_platform'
)


def extract_skills_from_jobs(db) -> Counter:
    """Extract all skills from tokenized jobs"""
    
    print("\n🔍 Extracting skills from jobs...")
    
    query = """
    SELECT id, tokens 
    FROM jobs 
    WHERE is_tokenized = TRUE 
    AND tokens IS NOT NULL
    """
    
    result = db.execute(text(query))
    rows = result.fetchall()
    
    print(f"   Found {len(rows):,} tokenized jobs")
    
    # Count skills
    skill_counter = Counter()
    skill_context = {}  # Store sample contexts
    
    for row in rows:
        job_id, tokens_data = row
        
        try:
            if isinstance(tokens_data, str):
                tokens = json.loads(tokens_data)
            else:
                tokens = tokens_data
            
            if 'skills' in tokens:
                skills_data = tokens['skills']
                
                if isinstance(skills_data, dict) and 'top' in skills_data:
                    # Handle current format: {"top": [...]}
                    top_skills = skills_data['top']
                    
                    if isinstance(top_skills, list):
                        for skill in top_skills:
                            if skill and isinstance(skill, str):
                                skill_normalized = skill.lower().strip()
                                skill_counter[skill_normalized] += 1
                                
                                # Store context sample (first 3 jobs)
                                if skill_normalized not in skill_context:
                                    skill_context[skill_normalized] = []
                                
                                if len(skill_context[skill_normalized]) < 3:
                                    skill_context[skill_normalized].append({
                                        'job_id': job_id,
                                        'original': skill
                                    })
        
        except Exception as e:
            continue
    
    print(f"   ✅ Found {len(skill_counter):,} unique skills")
    print(f"   ✅ Total occurrences: {sum(skill_counter.values()):,}")
    
    return skill_counter, skill_context


def populate_queue(
    db,
    skill_counter: Counter,
    skill_context: dict,
    limit: int = 1000,
    min_count: int = 2
):
    """Populate validation queue"""
    
    print(f"\n📥 Populating validation queue...")
    print(f"   Limit: {limit} skills")
    print(f"   Min count: {min_count} occurrences")
    
    # Filter by min_count
    filtered_skills = {
        skill: count 
        for skill, count in skill_counter.items() 
        if count >= min_count
    }
    
    print(f"   After filter: {len(filtered_skills):,} skills")
    
    # Get top N by frequency
    top_skills = skill_counter.most_common(limit)
    
    inserted = 0
    skipped = 0
    
    for skill, count in top_skills:
        if count < min_count:
            continue
        
        # Check if already in queue
        check = db.execute(
            text("SELECT id FROM validation_queue WHERE skill_name = :skill"),
            {'skill': skill}
        )
        
        if check.fetchone():
            skipped += 1
            continue
        
        # Prepare context sample
        context_sample = None
        if skill in skill_context:
            context_sample = json.dumps(skill_context[skill])
        
        # Calculate priority (higher count = higher priority)
        priority = min(count, 100)  # Cap at 100
        
        # Insert into queue
        db.execute(
            text("""
                INSERT INTO validation_queue 
                (skill_name, source_count, priority, status, context_sample)
                VALUES 
                (:skill_name, :source_count, :priority, 'pending', :context_sample)
            """),
            {
                'skill_name': skill,
                'source_count': count,
                'priority': priority,
                'context_sample': context_sample
            }
        )
        
        inserted += 1
        
        if inserted % 50 == 0:
            print(f"   Progress: {inserted}/{limit}")
    
    db.commit()
    
    print(f"\n   ✅ Inserted: {inserted}")
    print(f"   ⏭️  Skipped: {skipped} (already in queue)")
    
    return inserted, skipped


def show_queue_stats(db):
    """Show validation queue statistics"""
    
    print("\n📊 VALIDATION QUEUE STATISTICS")
    print("=" * 70)
    
    # Total in queue
    result = db.execute(text("SELECT COUNT(*) FROM validation_queue"))
    total = result.scalar()
    print(f"Total items in queue: {total:,}")
    
    # By status
    result = db.execute(text("""
        SELECT status, COUNT(*) as count
        FROM validation_queue
        GROUP BY status
        ORDER BY count DESC
    """))
    
    print(f"\nBy status:")
    for row in result:
        print(f"   {row[0]:15} {row[1]:>6,}")
    
    # Top 10 by priority
    result = db.execute(text("""
        SELECT skill_name, source_count, priority
        FROM validation_queue
        WHERE status = 'pending'
        ORDER BY priority DESC, source_count DESC
        LIMIT 10
    """))
    
    print(f"\nTop 10 pending (by priority):")
    for i, row in enumerate(result, 1):
        print(f"   {i:2}. {row[0]:<30} (count: {row[1]:>4}, priority: {row[2]:>3})")


def main(limit: int = 1000, min_count: int = 2):
    """Main execution"""
    
    print("\n" + "=" * 70)
    print("POPULATE VALIDATION QUEUE - MODULE #5")
    print("=" * 70)
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Extract skills
        skill_counter, skill_context = extract_skills_from_jobs(db)
        
        if not skill_counter:
            print("\n❌ No skills found in database!")
            print("   Make sure jobs are tokenized with skill data")
            return
        
        # Populate queue
        inserted, skipped = populate_queue(
            db, 
            skill_counter, 
            skill_context,
            limit=limit,
            min_count=min_count
        )
        
        # Show stats
        show_queue_stats(db)
        
        print("\n" + "=" * 70)
        print("✅ QUEUE POPULATION COMPLETE")
        print("=" * 70)
        
        print(f"\n💡 Next steps:")
        print(f"   1. Start validation interface")
        print(f"   2. Review skills in queue")
        print(f"   3. Categorize and validate")
        print(f"\n   Access queue at: /validation/queue")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate validation queue")
    parser.add_argument('--limit', type=int, default=1000, help='Max skills to add')
    parser.add_argument('--min-count', type=int, default=2, help='Min occurrence count')
    
    args = parser.parse_args()
    
    main(limit=args.limit, min_count=args.min_count)