"""
Job Title Tokenizer - Enhanced with Confidence Scoring
Handles data inconsistency between title and database fields

Usage:
    tokenizer = JobTitleTokenizer()
    result = tokenizer.tokenize_with_reconciliation(
        title="Senior Full Stack Developer",
        db_level="mid"  # Inconsistent data
    )
"""

from typing import Dict, Any, Optional, Tuple
from app.services.preprocessing.tokenizers.job_title_tokenizer import JobTitleTokenizer as BaseJobTitleTokenizer


class JobTitleTokenizerEnhanced(BaseJobTitleTokenizer):
    """Enhanced tokenizer with confidence scoring and data reconciliation"""
    
    def extract_level_with_confidence(self, title: str) -> Tuple[Optional[str], float]:
        """
        Extract job level with confidence score
        
        Args:
            title: Job title
            
        Returns:
            Tuple of (level, confidence_score)
            confidence_score: 0.0 to 1.0
        """
        if not title:
            return (None, 0.0)
        
        title_lower = title.lower()
        title_words = title_lower.split()
        
        # HIGH CONFIDENCE (0.90-0.95): Level word at start of title
        first_words = ' '.join(title_words[:2])  # First 2 words
        for level, keywords in self.levels.items():
            for keyword in keywords:
                if first_words.startswith(keyword):
                    return (level, 0.95)
        
        # MEDIUM-HIGH CONFIDENCE (0.75-0.85): Level word in first 3 words
        first_three = ' '.join(title_words[:3])
        for level, keywords in self.levels.items():
            for keyword in keywords:
                if keyword in first_three:
                    return (level, 0.80)
        
        # MEDIUM CONFIDENCE (0.60-0.70): Level word anywhere
        for level, keywords in self.levels.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return (level, 0.65)
        
        # LOW CONFIDENCE (0.0): No level detected
        return (None, 0.0)
    
    def reconcile_level(self, 
                       title: str, 
                       db_level: Optional[str] = None,
                       confidence_threshold: float = 0.75) -> Dict[str, Any]:
        """
        Reconcile level from title and database
        
        Args:
            title: Job title
            db_level: Level from database (may be inconsistent)
            confidence_threshold: Minimum confidence to trust title (default 0.75)
            
        Returns:
            Dictionary with reconciliation result
        """
        # Extract from title
        title_level, confidence = self.extract_level_with_confidence(title)
        
        # Decision logic
        decision_reason = ""
        final_level = None
        has_discrepancy = False
        
        # Case 1: High confidence from title
        if confidence >= confidence_threshold:
            final_level = title_level
            if db_level and db_level != title_level:
                has_discrepancy = True
                decision_reason = f"High confidence from title ({confidence:.0%}), overriding database"
            else:
                decision_reason = f"High confidence from title ({confidence:.0%})"
        
        # Case 2: Low confidence from title, use database
        elif db_level:
            final_level = db_level
            if title_level:
                has_discrepancy = True
                decision_reason = f"Low confidence from title ({confidence:.0%}), using database"
            else:
                decision_reason = "No level in title, using database"
        
        # Case 3: Low confidence and no database value
        else:
            final_level = title_level if title_level else "not_specified"
            decision_reason = "No reliable data available"
        
        return {
            'final_level': final_level,
            'title_level': title_level,
            'db_level': db_level,
            'confidence': confidence,
            'has_discrepancy': has_discrepancy,
            'decision_reason': decision_reason,
            'needs_review': has_discrepancy and confidence >= confidence_threshold
        }
    
    def tokenize_with_reconciliation(self, 
                                     title: str,
                                     db_level: Optional[str] = None,
                                     db_experience: Optional[str] = None) -> Dict[str, Any]:
        """
        Full tokenization with data reconciliation
        
        Args:
            title: Job title
            db_level: Level from database
            db_experience: Experience from database
            
        Returns:
            Complete tokenization result with reconciliation
        """
        # Base tokenization
        base_result = self.tokenize(title)
        
        # Reconcile level
        reconciliation = self.reconcile_level(title, db_level)
        
        # Update result
        base_result['level_reconciliation'] = reconciliation
        base_result['level'] = reconciliation['final_level']
        
        return base_result


# Helper function for easy use
def tokenize_job_title_smart(title: str, 
                              db_level: Optional[str] = None) -> Dict[str, Any]:
    """
    Smart job title tokenization with automatic reconciliation
    
    Args:
        title: Job title
        db_level: Existing level from database
        
    Returns:
        Tokenization result with reconciled level
    """
    tokenizer = JobTitleTokenizerEnhanced()
    return tokenizer.tokenize_with_reconciliation(title, db_level)


if __name__ == "__main__":
    # Test with inconsistent data
    tokenizer = JobTitleTokenizerEnhanced()
    
    print("=" * 70)
    print("ENHANCED JOB TITLE TOKENIZER - INCONSISTENCY HANDLING")
    print("=" * 70)
    print()
    
    test_cases = [
        ("Senior Full Stack Developer - Jakarta", "mid"),  # Inconsistent
        ("Junior Backend Developer", "junior"),  # Consistent
        ("Full Stack Developer", "senior"),  # Title missing level
        ("Lead Data Scientist", None),  # No DB data
        ("Developer", "senior"),  # Title ambiguous
    ]
    
    for title, db_level in test_cases:
        result = tokenizer.tokenize_with_reconciliation(title, db_level)
        recon = result['level_reconciliation']
        
        print(f"Title: {title}")
        print(f"DB Level: {db_level}")
        print(f"Title Level: {recon['title_level']} (confidence: {recon['confidence']:.0%})")
        print(f"Final Level: {recon['final_level']}")
        print(f"Decision: {recon['decision_reason']}")
        if recon['needs_review']:
            print(f"⚠️  NEEDS REVIEW: High-confidence discrepancy detected!")
        print("-" * 70)
