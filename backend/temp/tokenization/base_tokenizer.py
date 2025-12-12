"""
Base Tokenizer
Abstract base class for all specialized tokenizers

Usage:
    from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer
    
    class MyTokenizer(BaseTokenizer):
        def tokenize(self, text):
            # Implementation
            pass
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.services.preprocessing.text_cleaner import TextCleaner
from app.services.preprocessing.indonesian_nlp import IndonesianNLP


class BaseTokenizer(ABC):
    """Abstract base class for tokenizers"""
    
    def __init__(self, 
                 use_cleaner: bool = True,
                 use_indonesian_nlp: bool = True,
                 lowercase: bool = True):
        """
        Initialize base tokenizer
        
        Args:
            use_cleaner: Use TextCleaner for preprocessing
            use_indonesian_nlp: Use Indonesian NLP features
            lowercase: Convert to lowercase
        """
        self.use_cleaner = use_cleaner
        self.use_indonesian_nlp = use_indonesian_nlp
        self.lowercase = lowercase
        
        # Initialize tools
        if use_cleaner:
            self.cleaner = TextCleaner(lowercase=lowercase)
        
        if use_indonesian_nlp:
            self.indo_nlp = IndonesianNLP()
    
    @abstractmethod
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize text (must be implemented by subclasses)
        
        Args:
            text: Text to tokenize
            
        Returns:
            Dictionary with tokenization results
        """
        pass
    
    def preprocess(self, text: str) -> Optional[str]:
        """
        Preprocess text before tokenization
        
        Args:
            text: Raw text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return None
        
        # Clean text
        if self.use_cleaner:
            text = self.cleaner.clean(text)
        
        # Normalize Indonesian slang
        if self.use_indonesian_nlp:
            text = self.indo_nlp.normalize_slang(text)
            text = self.indo_nlp.normalize_job_terms(text)
        
        return text
    
    def split_tokens(self, text: str, delimiter: str = None) -> List[str]:
        """
        Split text into tokens
        
        Args:
            text: Text to split
            delimiter: Delimiter to split on (None = whitespace)
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        if delimiter:
            tokens = [t.strip() for t in text.split(delimiter) if t.strip()]
        else:
            tokens = text.split()
        
        return tokens
    
    def extract_keywords(self, tokens: List[str], top_n: int = 10) -> List[str]:
        """
        Extract top keywords from tokens (simple frequency-based)
        
        Args:
            tokens: List of tokens
            top_n: Number of top keywords to return
            
        Returns:
            List of top keywords
        """
        if not tokens:
            return []
        
        # Count frequency
        freq = {}
        for token in tokens:
            token_lower = token.lower() if self.lowercase else token
            freq[token_lower] = freq.get(token_lower, 0) + 1
        
        # Sort by frequency
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N
        return [token for token, count in sorted_tokens[:top_n]]
    
    def validate_input(self, text: str) -> bool:
        """
        Validate input text
        
        Args:
            text: Text to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        # Check if text has content after stripping
        if not text.strip():
            return False
        
        return True
    
    def get_token_count(self, text: str) -> int:
        """
        Get token count
        
        Args:
            text: Text to count tokens
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        return len(self.split_tokens(text))
    
    def to_dict(self, result: Any) -> Dict[str, Any]:
        """
        Convert result to dictionary format
        
        Args:
            result: Tokenization result
            
        Returns:
            Dictionary representation
        """
        if isinstance(result, dict):
            return result
        
        return {'result': result}


class TokenizerResult:
    """Container for tokenization results"""
    
    def __init__(self, 
                 tokens: List[str],
                 original_text: str,
                 normalized_text: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize TokenizerResult
        
        Args:
            tokens: List of tokens
            original_text: Original input text
            normalized_text: Normalized version of text
            metadata: Additional metadata
        """
        self.tokens = tokens
        self.original_text = original_text
        self.normalized_text = normalized_text or original_text
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tokens': self.tokens,
            'token_count': len(self.tokens),
            'original_text': self.original_text,
            'normalized_text': self.normalized_text,
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        return f"TokenizerResult(tokens={len(self.tokens)}, text='{self.original_text[:50]}...')"


if __name__ == "__main__":
    # Test base tokenizer
    class SimpleTokenizer(BaseTokenizer):
        def tokenize(self, text: str) -> Dict[str, Any]:
            """Simple word tokenization"""
            if not self.validate_input(text):
                return {'tokens': [], 'error': 'Invalid input'}
            
            # Preprocess
            cleaned = self.preprocess(text)
            
            # Tokenize
            tokens = self.split_tokens(cleaned)
            
            # Create result
            result = TokenizerResult(
                tokens=tokens,
                original_text=text,
                normalized_text=cleaned,
                metadata={'token_count': len(tokens)}
            )
            
            return result.to_dict()
    
    # Test
    tokenizer = SimpleTokenizer()
    text = "Kami mencari Full-Stack Developer yg berpengalaman"
    result = tokenizer.tokenize(text)
    
    print("Result:", result)
    print("Tokens:", result['tokens'])
    print("Count:", result['token_count'])
