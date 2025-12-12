"""
Job Title Tokenizer
Extracts structured information from job titles

Features:
- Extract job level (junior, senior, manager, etc)
- Extract job role/position
- Extract location (if mentioned in title)
- Normalize variations

Usage:
    from app.services.preprocessing.tokenizers.job_title_tokenizer import JobTitleTokenizer
    
    tokenizer = JobTitleTokenizer()
    result = tokenizer.tokenize("Senior Full Stack Developer - Jakarta")
"""

import re
from typing import Dict, Any, Optional, List
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer, TokenizerResult


class JobTitleTokenizer(BaseTokenizer):
    """Tokenize and extract information from job titles"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=True)
        
        # Define job levels
        self.levels = {
            'junior': ['junior', 'jr', 'pemula', 'fresh graduate', 'entry level'],
            'senior': ['senior', 'sr', 'berpengalaman', 'experienced'],
            'lead': ['lead', 'principal', 'kepala'],
            'manager': ['manager', 'manajer', 'mgr', 'head'],
            'supervisor': ['supervisor', 'spv', 'pengawas'],
            'director': ['director', 'direktur', 'dir'],
            'vp': ['vp', 'vice president', 'wakil direktur'],
            'c-level': ['ceo', 'cto', 'cfo', 'coo', 'cio', 'cmo'],
            'staff': ['staff', 'staf'],
            'assistant': ['assistant', 'asisten', 'asst'],
            'associate': ['associate', 'asosiasi'],
            'intern': ['intern', 'magang', 'internship'],
        }
        
        # Common job roles
        self.common_roles = [
            'developer', 'programmer', 'engineer', 'designer', 'analyst',
            'manager', 'administrator', 'specialist', 'coordinator', 'consultant',
            'representative', 'officer', 'executive', 'assistant', 'technician',
            'architect', 'scientist', 'researcher', 'writer', 'editor',
        ]
        
        # Technology/domain prefixes
        self.tech_prefixes = [
            'software', 'web', 'mobile', 'frontend', 'backend', 'fullstack', 'full stack',
            'data', 'machine learning', 'ai', 'devops', 'cloud', 'security',
            'network', 'system', 'database', 'qa', 'quality assurance',
        ]
    
    def extract_level(self, title: str) -> Optional[str]:
        """
        Extract job level from title
        
        Args:
            title: Job title
            
        Returns:
            Job level or None
        """
        title_lower = title.lower()
        
        for level, keywords in self.levels.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return level
        
        return None
    
    def extract_role(self, title: str) -> Optional[str]:
        """
        Extract primary job role
        
        Args:
            title: Job title
            
        Returns:
            Job role
        """
        title_lower = title.lower()
        
        # Find common roles
        found_roles = []
        for role in self.common_roles:
            if role in title_lower:
                found_roles.append(role)
        
        # Return first found role
        if found_roles:
            return found_roles[0]
        
        # If no common role found, extract main noun phrase
        # Remove level keywords
        cleaned = title_lower
        for level_keywords in self.levels.values():
            for keyword in level_keywords:
                cleaned = cleaned.replace(keyword, '')
        
        # Remove location indicators
        cleaned = re.sub(r'\s*[-–]\s*\w+\s*$', '', cleaned)
        
        # Clean and return
        cleaned = cleaned.strip()
        if cleaned:
            tokens = cleaned.split()
            # Return last 2-3 words as role
            return ' '.join(tokens[-2:]) if len(tokens) >= 2 else cleaned
        
        return None
    
    def extract_location(self, title: str) -> Optional[str]:
        """
        Extract location if mentioned in title
        
        Args:
            title: Job title
            
        Returns:
            Location or None
        """
        # Pattern: "- Location" or "(Location)"
        
        # Pattern 1: Dash separator
        match = re.search(r'[-–]\s*([A-Za-z\s]+)\s*$', title)
        if match:
            location = match.group(1).strip()
            # Check if it's a valid location (simple heuristic)
            if len(location.split()) <= 3:  # Max 3 words
                return location
        
        # Pattern 2: Parentheses
        match = re.search(r'\(([A-Za-z\s]+)\)', title)
        if match:
            location = match.group(1).strip()
            if len(location.split()) <= 3:
                return location
        
        return None
    
    def extract_tech_stack(self, title: str) -> List[str]:
        """
        Extract technology/domain from title
        
        Args:
            title: Job title
            
        Returns:
            List of technologies
        """
        title_lower = title.lower()
        tech_found = []
        
        for tech in self.tech_prefixes:
            if tech in title_lower:
                tech_found.append(tech)
        
        # Also extract from parentheses or slashes
        # Example: "Developer (React/Node.js)"
        tech_in_parens = re.findall(r'\(([^)]+)\)', title)
        for tech_group in tech_in_parens:
            techs = re.split(r'[/,&]', tech_group)
            tech_found.extend([t.strip().lower() for t in techs if t.strip()])
        
        return tech_found
    
    def normalize_title(self, title: str) -> str:
        """
        Normalize job title
        
        Args:
            title: Raw job title
            
        Returns:
            Normalized title
        """
        # Clean
        cleaned = self.preprocess(title)
        
        if not cleaned:
            return ""
        
        # Remove location part
        cleaned = re.sub(r'\s*[-–]\s*\w+\s*$', '', cleaned)
        
        # Remove content in parentheses (usually tech stack)
        cleaned = re.sub(r'\s*\([^)]+\)', '', cleaned)
        
        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize job title
        
        Args:
            text: Job title
            
        Returns:
            Dictionary with extracted information
        """
        if not self.validate_input(text):
            return {
                'tokens': [],
                'level': None,
                'role': None,
                'location': None,
                'tech_stack': [],
                'normalized': None,
                'original': text,
                'error': 'Invalid input'
            }
        
        # Extract information
        level = self.extract_level(text)
        role = self.extract_role(text)
        location = self.extract_location(text)
        tech_stack = self.extract_tech_stack(text)
        normalized = self.normalize_title(text)
        
        # Tokenize normalized title
        tokens = self.split_tokens(normalized)
        
        # Build result
        result = {
            'tokens': tokens,
            'token_count': len(tokens),
            'level': level,
            'role': role,
            'location': location,
            'tech_stack': tech_stack,
            'normalized': normalized,
            'original': text,
            'metadata': {
                'has_level': level is not None,
                'has_location': location is not None,
                'has_tech': len(tech_stack) > 0
            }
        }
        
        return result


if __name__ == "__main__":
    # Test examples
    tokenizer = JobTitleTokenizer()
    
    test_titles = [
        "Senior Full Stack Developer - Jakarta",
        "Frontend Engineer (React/Vue.js)",
        "Data Scientist - Machine Learning",
        "Junior Backend Developer",
        "Manager IT Infrastructure",
        "Magang UI/UX Designer",
        "Full-Stack Developer (Python/Django) - Surabaya",
    ]
    
    print("=" * 70)
    print("JOB TITLE TOKENIZER TEST")
    print("=" * 70)
    print()
    
    for title in test_titles:
        result = tokenizer.tokenize(title)
        
        print(f"Original:   {result['original']}")
        print(f"Normalized: {result['normalized']}")
        print(f"Level:      {result['level']}")
        print(f"Role:       {result['role']}")
        print(f"Location:   {result['location']}")
        print(f"Tech:       {result['tech_stack']}")
        print(f"Tokens:     {result['tokens']}")
        print("-" * 70)
