"""
Text Cleaner Module
Handles basic text cleaning and normalization for Indonesian job postings

Usage:
    from app.services.preprocessing.text_cleaner import TextCleaner
    
    cleaner = TextCleaner()
    clean_text = cleaner.clean("Raw text here...")
"""

import re
import html
from typing import Optional


class TextCleaner:
    """Clean and normalize text data"""
    
    def __init__(self, 
                 remove_html: bool = True,
                 remove_urls: bool = True,
                 remove_emails: bool = True,
                 remove_numbers: bool = False,
                 lowercase: bool = False):
        """
        Initialize TextCleaner
        
        Args:
            remove_html: Remove HTML/XML tags
            remove_urls: Remove URLs
            remove_emails: Remove email addresses
            remove_numbers: Remove all numbers
            lowercase: Convert to lowercase
        """
        self.remove_html = remove_html
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_numbers = remove_numbers
        self.lowercase = lowercase
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns"""
        # HTML tags
        self.html_pattern = re.compile(r'<[^>]+>')
        
        # URLs
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Emails
        self.email_pattern = re.compile(r'\S+@\S+')
        
        # Numbers (standalone)
        self.number_pattern = re.compile(r'\b\d+\b')
        
        # Multiple spaces
        self.space_pattern = re.compile(r'\s+')
        
        # Special characters (keep basic punctuation)
        self.special_char_pattern = re.compile(r'[^a-zA-Z0-9\s.,;:!?()\-\'\"]+')
    
    def clean(self, text: str) -> Optional[str]:
        """
        Clean text with all enabled options
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text or None if input is empty
        """
        if not text or not isinstance(text, str):
            return None
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        if self.remove_html:
            text = self.html_pattern.sub(' ', text)
        
        # Remove URLs
        if self.remove_urls:
            text = self.url_pattern.sub(' ', text)
        
        # Remove emails
        if self.remove_emails:
            text = self.email_pattern.sub(' ', text)
        
        # Remove numbers
        if self.remove_numbers:
            text = self.number_pattern.sub(' ', text)
        
        # Remove special characters (keep basic punctuation)
        text = self.special_char_pattern.sub(' ', text)
        
        # Normalize whitespace
        text = self.space_pattern.sub(' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        return text if text else None
    
    def remove_extra_whitespace(self, text: str) -> str:
        """Remove multiple spaces and normalize whitespace"""
        if not text:
            return ""
        return self.space_pattern.sub(' ', text).strip()
    
    def remove_html_tags(self, text: str) -> str:
        """Remove HTML/XML tags from text"""
        if not text:
            return ""
        return self.html_pattern.sub(' ', text)
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        if not text:
            return ""
        return self.url_pattern.sub(' ', text)
    
    def remove_emails(self, text: str) -> str:
        """Remove email addresses from text"""
        if not text:
            return ""
        return self.email_pattern.sub(' ', text)
    
    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation (remove duplicates)"""
        if not text:
            return ""
        
        # Remove duplicate punctuation
        text = re.sub(r'([.,;:!?])\1+', r'\1', text)
        
        # Add space after punctuation if missing
        text = re.sub(r'([.,;:!?])([a-zA-Z])', r'\1 \2', text)
        
        return text
    
    def clean_job_title(self, title: str) -> Optional[str]:
        """
        Clean job title specifically
        
        Args:
            title: Raw job title
            
        Returns:
            Cleaned title
        """
        if not title:
            return None
        
        # Basic cleaning (no HTML, URLs in titles usually)
        text = title.strip()
        
        # Remove special characters but keep hyphen and slash
        text = re.sub(r'[^a-zA-Z0-9\s\-/()&]', ' ', text)
        
        # Normalize whitespace
        text = self.space_pattern.sub(' ', text).strip()
        
        return text if text else None
    
    def clean_job_description(self, description: str) -> Optional[str]:
        """
        Clean job description
        
        Args:
            description: Raw job description
            
        Returns:
            Cleaned description
        """
        if not description:
            return None
        
        # Full cleaning
        cleaner = TextCleaner(
            remove_html=True,
            remove_urls=True,
            remove_emails=True,
            remove_numbers=False,  # Keep numbers in descriptions
            lowercase=False
        )
        
        return cleaner.clean(description)
    
    def clean_skills(self, skills: str) -> Optional[str]:
        """
        Clean skills field
        
        Args:
            skills: Raw skills text (comma-separated or multiline)
            
        Returns:
            Cleaned skills
        """
        if not skills:
            return None
        
        # Remove HTML
        text = self.html_pattern.sub(' ', skills)
        
        # Keep basic punctuation (comma, semicolon for separators)
        text = re.sub(r'[^a-zA-Z0-9\s,;.+#()\-/]', ' ', text)
        
        # Normalize whitespace
        text = self.space_pattern.sub(' ', text).strip()
        
        return text if text else None


# Convenience functions
def clean_text(text: str, **kwargs) -> Optional[str]:
    """
    Quick text cleaning function
    
    Args:
        text: Text to clean
        **kwargs: Options for TextCleaner
        
    Returns:
        Cleaned text
    """
    cleaner = TextCleaner(**kwargs)
    return cleaner.clean(text)


def clean_job_title(title: str) -> Optional[str]:
    """Quick job title cleaning"""
    cleaner = TextCleaner()
    return cleaner.clean_job_title(title)


def clean_job_description(description: str) -> Optional[str]:
    """Quick job description cleaning"""
    cleaner = TextCleaner()
    return cleaner.clean_job_description(description)


def clean_skills(skills: str) -> Optional[str]:
    """Quick skills cleaning"""
    cleaner = TextCleaner()
    return cleaner.clean_skills(skills)


if __name__ == "__main__":
    # Test examples
    cleaner = TextCleaner(lowercase=True)
    
    # Test job title
    title = "Senior Full-Stack Developer (React/Node.js) - Jakarta"
    print(f"Original: {title}")
    print(f"Cleaned: {cleaner.clean_job_title(title)}")
    print()
    
    # Test description with HTML
    desc = "<p>We are looking for a <b>Python Developer</b>. Email: job@company.com Visit: https://company.com</p>"
    print(f"Original: {desc}")
    print(f"Cleaned: {cleaner.clean(desc)}")
    print()
    
    # Test skills
    skills = "Python, Java, React.js, MySQL, Docker & Kubernetes"
    print(f"Original: {skills}")
    print(f"Cleaned: {cleaner.clean_skills(skills)}")
