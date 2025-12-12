"""
Qualification Tokenizer
Extracts and categorizes job qualifications/requirements

Features:
- Parse education requirements
- Parse experience requirements
- Parse certification requirements
- Extract required vs preferred qualifications

Usage:
    from app.services.preprocessing.tokenizers.qualification_tokenizer import QualificationTokenizer
    
    tokenizer = QualificationTokenizer()
    result = tokenizer.tokenize(qualifications_text)
"""

import re
from typing import Dict, Any, List, Optional
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer


class QualificationTokenizer(BaseTokenizer):
    """Tokenize job qualifications"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=True)
        
        # Education levels
        self.education_levels = {
            'sma': 'SMA/SMK',
            'smk': 'SMA/SMK',
            'd3': 'D3',
            'diploma': 'D3',
            's1': 'S1',
            'sarjana': 'S1',
            'bachelor': 'S1',
            's2': 'S2',
            'magister': 'S2',
            'master': 'S2',
            's3': 'S3',
            'doktor': 'S3',
            'phd': 'S3',
        }
    
    def parse_bullet_points(self, text: str) -> List[str]:
        """Parse qualification bullet points"""
        if not text:
            return []
        
        bullets = []
        
        # Bullet symbols
        pattern1 = r'[•·\-\*]\s*(.+?)(?=\n[•·\-\*]|\Z)'
        matches1 = re.findall(pattern1, text, re.DOTALL)
        bullets.extend([m.strip() for m in matches1 if m.strip()])
        
        # Numbered lists
        pattern2 = r'\d+\.\s*(.+?)(?=\n\d+\.|\Z)'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        bullets.extend([m.strip() for m in matches2 if m.strip()])
        
        # If no bullets, split by newlines
        if not bullets:
            lines = text.split('\n')
            bullets = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        
        # Clean bullets
        cleaned = []
        for bullet in bullets:
            bullet = ' '.join(bullet.split())
            if len(bullet) > 10:
                cleaned.append(bullet)
        
        return cleaned
    
    def extract_education(self, qualification: str) -> Optional[str]:
        """
        Extract education requirement
        
        Args:
            qualification: Qualification text
            
        Returns:
            Education level
        """
        qual_lower = qualification.lower()
        
        for edu_key, edu_level in self.education_levels.items():
            if edu_key in qual_lower:
                return edu_level
        
        return None
    
    def extract_experience(self, qualification: str) -> Optional[Dict[str, Any]]:
        """
        Extract experience requirement
        
        Args:
            qualification: Qualification text
            
        Returns:
            Dictionary with experience info
        """
        qual_lower = qualification.lower()
        
        # Patterns for experience
        patterns = [
            r'(\d+)\s*(?:\+)?\s*(?:tahun|thn|years?|yrs?)',  # "3 tahun", "2+ years"
            r'minimal\s+(\d+)\s+(?:tahun|thn|years?)',        # "minimal 3 tahun"
            r'pengalaman\s+(\d+)\s+(?:tahun|thn)',           # "pengalaman 3 tahun"
            r'experience\s+(?:of\s+)?(\d+)\s+(?:years?)',    # "experience of 3 years"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, qual_lower)
            if match:
                years = int(match.group(1))
                return {
                    'years': years,
                    'text': match.group(0)
                }
        
        # Check for fresh graduate / entry level
        fresh_keywords = ['fresh graduate', 'entry level', 'tanpa pengalaman', 'no experience']
        if any(kw in qual_lower for kw in fresh_keywords):
            return {
                'years': 0,
                'text': 'fresh graduate'
            }
        
        return None
    
    def extract_certifications(self, qualification: str) -> List[str]:
        """
        Extract certification requirements
        
        Args:
            qualification: Qualification text
            
        Returns:
            List of certifications
        """
        qual_lower = qualification.lower()
        
        # Common certifications
        certs = []
        
        cert_patterns = [
            r'\b(aws|azure|gcp|google cloud)\s+certified\b',
            r'\b(pmp|scrum master|agile)\s+certi(?:fication|fied)?\b',
            r'\bcerti(?:fication|fied)\s+(?:in\s+)?(\w+)\b',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, qual_lower)
            certs.extend(matches)
        
        return certs
    
    def is_required(self, qualification: str) -> bool:
        """
        Check if qualification is required or preferred
        
        Args:
            qualification: Qualification text
            
        Returns:
            True if required
        """
        qual_lower = qualification.lower()
        
        # Required keywords
        required_keywords = [
            'wajib', 'required', 'must', 'harus', 'mandatory',
            'minimal', 'minimum', 'at least'
        ]
        
        # Preferred keywords
        preferred_keywords = [
            'preferred', 'nice to have', 'plus', 'advantage',
            'lebih disukai', 'diutamakan', 'optional'
        ]
        
        # Check preferred first (to override required)
        if any(kw in qual_lower for kw in preferred_keywords):
            return False
        
        # Check required
        if any(kw in qual_lower for kw in required_keywords):
            return True
        
        # Default: assume required
        return True
    
    def categorize_qualification(self, qualification: str) -> str:
        """
        Categorize qualification type
        
        Args:
            qualification: Qualification text
            
        Returns:
            Category name
        """
        qual_lower = qualification.lower()
        
        # Education
        if any(edu in qual_lower for edu in self.education_levels.keys()):
            return 'education'
        
        # Experience
        if any(kw in qual_lower for kw in ['pengalaman', 'experience', 'tahun', 'years']):
            return 'experience'
        
        # Technical skill
        if any(kw in qual_lower for kw in ['menguasai', 'familiar', 'proficient', 'knowledge of']):
            return 'technical_skill'
        
        # Soft skill
        if any(kw in qual_lower for kw in ['komunikasi', 'teamwork', 'leadership', 'analytical']):
            return 'soft_skill'
        
        # Certification
        if any(kw in qual_lower for kw in ['sertifikat', 'certification', 'certified']):
            return 'certification'
        
        return 'other'
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize qualifications text
        
        Args:
            text: Qualifications text
            
        Returns:
            Dictionary with parsed qualifications
        """
        if not self.validate_input(text):
            return {
                'qualifications': [],
                'count': 0,
                'education': None,
                'experience': None,
                'certifications': [],
                'required': [],
                'preferred': [],
                'categorized': {},
                'original': text,
                'error': 'Invalid input'
            }
        
        # Parse bullets
        bullets = self.parse_bullet_points(text)
        
        # Analyze each qualification
        qual_data = []
        education_found = None
        experience_found = None
        certifications_found = []
        required_quals = []
        preferred_quals = []
        categorized = {}
        
        for bullet in bullets:
            # Extract info
            education = self.extract_education(bullet)
            experience = self.extract_experience(bullet)
            certs = self.extract_certifications(bullet)
            is_required = self.is_required(bullet)
            category = self.categorize_qualification(bullet)
            
            # Build data
            qual_info = {
                'text': bullet,
                'category': category,
                'is_required': is_required,
                'education': education,
                'experience': experience,
                'certifications': certs
            }
            qual_data.append(qual_info)
            
            # Collect specific info
            if education and not education_found:
                education_found = education
            
            if experience and not experience_found:
                experience_found = experience
            
            if certs:
                certifications_found.extend(certs)
            
            # Split by requirement level
            if is_required:
                required_quals.append(bullet)
            else:
                preferred_quals.append(bullet)
            
            # Group by category
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(bullet)
        
        # Build result
        result = {
            'qualifications': qual_data,
            'count': len(qual_data),
            'education': education_found,
            'experience': experience_found,
            'certifications': list(set(certifications_found)),
            'required': required_quals,
            'preferred': preferred_quals,
            'categorized': categorized,
            'original': text[:200] + '...' if len(text) > 200 else text,
            'metadata': {
                'has_education': education_found is not None,
                'has_experience': experience_found is not None,
                'has_certifications': len(certifications_found) > 0,
                'required_count': len(required_quals),
                'preferred_count': len(preferred_quals),
                'categories': list(categorized.keys())
            }
        }
        
        return result


if __name__ == "__main__":
    # Test
    tokenizer = QualificationTokenizer()
    
    test_text = """
    • Minimal S1 Teknik Informatika atau setara
    • Pengalaman minimal 3 tahun sebagai Full Stack Developer
    • Menguasai JavaScript, React, Node.js (wajib)
    • Familiar dengan Docker dan Kubernetes (preferred)
    • Memiliki sertifikasi AWS (nice to have)
    • Kemampuan komunikasi yang baik
    """
    
    result = tokenizer.tokenize(test_text)
    
    print("=" * 70)
    print("QUALIFICATION TOKENIZER TEST")
    print("=" * 70)
    print()
    print(f"Total qualifications: {result['count']}")
    print(f"Education: {result['education']}")
    print(f"Experience: {result['experience']}")
    print(f"Certifications: {result['certifications']}")
    print(f"Required: {len(result['required'])}")
    print(f"Preferred: {len(result['preferred'])}")
    print(f"Categories: {list(result['categorized'].keys())}")
    print()
    print("Parsed qualifications:")
    for i, qual in enumerate(result['qualifications'][:3], 1):
        print(f"{i}. {qual['text'][:60]}...")
        print(f"   Category: {qual['category']}")
        print(f"   Required: {qual['is_required']}")
