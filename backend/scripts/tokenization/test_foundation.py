"""
Test foundation components
Run: python test_foundation.py
"""

import sys
import os
from pathlib import Path

# Add backend root to Python path
# Current file: backend/scripts/database_schema/seed_initial_data.py
# We need: backend/
backend_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_root))

from app.services.preprocessing.text_cleaner import TextCleaner
from app.services.preprocessing.indonesian_nlp import IndonesianNLP
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer

def test_text_cleaner():
    print("=" * 60)
    print("Testing TextCleaner")
    print("=" * 60)
    
    cleaner = TextCleaner(lowercase=True)
    
    # Test 1: Job title
    title = "Senior Full-Stack Developer (React/Node.js) - Jakarta"
    cleaned = cleaner.clean_job_title(title)
    print(f"Original: {title}")
    print(f"Cleaned:  {cleaned}")
    print()
    
    # Test 2: Description with HTML
    desc = "<p>We are looking for <b>Python Developer</b>. Email: job@company.com</p>"
    cleaned = cleaner.clean(desc)
    print(f"Original: {desc}")
    print(f"Cleaned:  {cleaned}")
    print()
    
    print("✓ TextCleaner working!\n")

def test_indonesian_nlp():
    print("=" * 60)
    print("Testing IndonesianNLP")
    print("=" * 60)
    
    nlp = IndonesianNLP()
    
    # Test 1: Slang normalization
    text = "Kami mencari developer yg berpengalaman min 2 thn"
    normalized = nlp.normalize_slang(text)
    print(f"Original:   {text}")
    print(f"Normalized: {normalized}")
    print()
    
    # Test 2: Tokenization
    text2 = "Dibutuhkan Full-Stack Developer untuk project website"
    tokens = nlp.tokenize(text2)
    print(f"Original: {text2}")
    print(f"Tokens:   {tokens}")
    print()
    
    print("✓ IndonesianNLP working!\n")

def test_base_tokenizer():
    print("=" * 60)
    print("Testing BaseTokenizer")
    print("=" * 60)
    
    # Create simple tokenizer
    class SimpleTokenizer(BaseTokenizer):
        def tokenize(self, text):
            if not self.validate_input(text):
                return {'error': 'Invalid input'}
            
            cleaned = self.preprocess(text)
            tokens = self.split_tokens(cleaned)
            
            return {
                'tokens': tokens,
                'token_count': len(tokens),
                'original': text,
                'normalized': cleaned
            }
    
    tokenizer = SimpleTokenizer()
    text = "Kami mencari Full-Stack Developer yg berpengalaman"
    result = tokenizer.tokenize(text)
    
    print(f"Original: {text}")
    print(f"Tokens:   {result['tokens']}")
    print(f"Count:    {result['token_count']}")
    print()
    
    print("✓ BaseTokenizer working!\n")

if __name__ == "__main__":
    print("\n")
    print("=" * 60)
    print("PHASE 4: TOKENIZATION - FOUNDATION TEST")
    print("=" * 60)
    print("\n")
    
    try:
        test_text_cleaner()
        test_indonesian_nlp()
        test_base_tokenizer()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nFoundation components working correctly!")
        print("Ready to build specialized tokenizers.\n")
        
    except Exception as e:
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()