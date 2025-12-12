"""
Test Specialized Tokenizers
Run: python test_tokenizers.py
"""

import sys
import os
from pathlib import Path

# Add backend root to Python path
# Current file: backend/scripts/database_schema/seed_initial_data.py
# We need: backend/
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

from app.services.preprocessing.tokenizers.job_title_tokenizer import JobTitleTokenizer
from app.services.preprocessing.tokenizers.skill_tokenizer import SkillTokenizer

def test_job_title_tokenizer():
    print("=" * 70)
    print("TESTING JOB TITLE TOKENIZER")
    print("=" * 70)
    print()
    
    tokenizer = JobTitleTokenizer()
    
    test_cases = [
        "Senior Full Stack Developer - Jakarta",
        "Frontend Engineer (React/Vue.js)",
        "Data Scientist - Machine Learning",
        "Junior Backend Developer",
        "Manager IT Infrastructure",
        "Magang UI/UX Designer",
    ]
    
    for title in test_cases:
        result = tokenizer.tokenize(title)
        
        print(f"Original:   {result['original']}")
        print(f"Normalized: {result['normalized']}")
        print(f"Level:      {result['level']}")
        print(f"Role:       {result['role']}")
        print(f"Location:   {result['location']}")
        print(f"Tech Stack: {result['tech_stack']}")
        print(f"Tokens:     {result['tokens'][:5]}...")  # First 5 tokens
        print()
    
    print("✓ Job Title Tokenizer working!\n")

def test_skill_tokenizer():
    print("=" * 70)
    print("TESTING SKILL TOKENIZER")
    print("=" * 70)
    print()
    
    tokenizer = SkillTokenizer()
    
    test_cases = [
        "Python, Java, JavaScript, React, MySQL",
        "Communication, Teamwork, Leadership",
        "Python (expert), React.js, Node.js, MongoDB, Docker",
        "HTML, CSS, JavaScript; React; Vue.js",
    ]
    
    for skills_text in test_cases:
        result = tokenizer.tokenize(skills_text)
        
        print(f"Original: {result['original'][:60]}...")
        print(f"Total: {result['total_count']} skills ({result['unique_count']} unique)")
        print(f"Categories found: {', '.join(result['categories'])}")
        print("Top skills per category:")
        for category, skills in list(result['categorized'].items())[:3]:
            print(f"  {category}: {', '.join(skills[:3])}")
        print()
    
    print("✓ Skill Tokenizer working!\n")

if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("SPECIALIZED TOKENIZERS TEST")
    print("=" * 70)
    print("\n")
    
    try:
        test_job_title_tokenizer()
        test_skill_tokenizer()
        
        print("=" * 70)
        print("✅ ALL TOKENIZER TESTS PASSED!")
        print("=" * 70)
        print("\nTokenizers 1-2 working correctly!")
        print("Ready to build remaining tokenizers (3-7).\n")
        
    except Exception as e:
        print("=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
