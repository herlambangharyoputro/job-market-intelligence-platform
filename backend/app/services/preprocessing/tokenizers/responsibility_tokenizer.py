"""
Responsibility Tokenizer
Extracts and categorizes job responsibilities

Features:
- Parse bullet points
- Extract action verbs
- Categorize responsibilities
- Detect seniority level from responsibilities

Usage:
    from app.services.preprocessing.tokenizers.responsibility_tokenizer import ResponsibilityTokenizer
    
    tokenizer = ResponsibilityTokenizer()
    result = tokenizer.tokenize(responsibilities_text)
"""

import re
from typing import Dict, Any, List, Set
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer


class ResponsibilityTokenizer(BaseTokenizer):
    """Tokenize job responsibilities"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=True)
        
        # Action verbs
        self.action_verbs = self._load_action_verbs()
        
        # Responsibility categories
        self.resp_categories = self._load_categories()
    
    def _load_action_verbs(self) -> Dict[str, Set[str]]:
        """Load action verbs by category"""
        return {
            'development': {
                'develop', 'mengembangkan', 'build', 'membangun', 'create', 'membuat',
                'implement', 'mengimplementasikan', 'code', 'coding', 'program', 'programming',
                'design', 'mendesain', 'architect', 'merancang', 'construct', 'write', 'menulis'
            },
            'management': {
                'manage', 'mengelola', 'lead', 'memimpin', 'coordinate', 'mengkoordinasikan',
                'supervise', 'mengawasi', 'organize', 'mengorganisir', 'plan', 'merencanakan',
                'direct', 'mengarahkan', 'oversee', 'mengawasi', 'control', 'mengontrol'
            },
            'analysis': {
                'analyze', 'menganalisis', 'research', 'meneliti', 'investigate', 'menginvestigasi',
                'evaluate', 'mengevaluasi', 'assess', 'menilai', 'review', 'mengulas',
                'study', 'mempelajari', 'examine', 'memeriksa', 'test', 'menguji'
            },
            'communication': {
                'communicate', 'berkomunikasi', 'present', 'mempresentasikan',
                'collaborate', 'berkolaborasi', 'coordinate', 'berkoordinasi',
                'discuss', 'mendiskusikan', 'report', 'melaporkan', 'document', 'mendokumentasikan',
                'meeting', 'rapat', 'explain', 'menjelaskan'
            },
            'maintenance': {
                'maintain', 'memelihara', 'support', 'mendukung', 'troubleshoot', 'mengatasi',
                'fix', 'memperbaiki', 'update', 'memperbarui', 'upgrade', 'mengupgrade',
                'optimize', 'mengoptimalkan', 'monitor', 'memantau', 'ensure', 'memastikan'
            },
            'training': {
                'train', 'melatih', 'mentor', 'membimbing', 'teach', 'mengajar',
                'guide', 'memandu', 'coach', 'melatih', 'educate', 'mengedukasi'
            }
        }
    
    def _load_categories(self) -> Dict[str, List[str]]:
        """Load responsibility category keywords"""
        return {
            'technical': ['code', 'develop', 'programming', 'system', 'database', 'api', 'software'],
            'leadership': ['lead', 'manage', 'team', 'coordinate', 'supervise', 'direct'],
            'analytical': ['analyze', 'research', 'data', 'report', 'metrics', 'evaluate'],
            'collaborative': ['collaborate', 'work with', 'coordinate', 'meeting', 'communicate'],
            'operational': ['maintain', 'support', 'monitor', 'ensure', 'implement', 'execute'],
        }
    
    def parse_bullet_points(self, text: str) -> List[str]:
        """
        Parse bullet points from text
        
        Args:
            text: Responsibilities text
            
        Returns:
            List of responsibility items
        """
        if not text:
            return []
        
        bullets = []
        
        # Pattern 1: Bullet symbols (•, -, *)
        pattern1 = r'[•·\-\*]\s*(.+?)(?=\n[•·\-\*]|\Z)'
        matches1 = re.findall(pattern1, text, re.DOTALL)
        bullets.extend([m.strip() for m in matches1 if m.strip()])
        
        # Pattern 2: Numbered lists (1., 2., etc)
        pattern2 = r'\d+\.\s*(.+?)(?=\n\d+\.|\Z)'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        bullets.extend([m.strip() for m in matches2 if m.strip()])
        
        # If no bullets found, split by newlines
        if not bullets:
            lines = text.split('\n')
            bullets = [line.strip() for line in lines if line.strip() and len(line.strip()) > 20]
        
        # Clean each bullet (remove extra newlines within bullet)
        cleaned_bullets = []
        for bullet in bullets:
            bullet = ' '.join(bullet.split())  # Normalize whitespace
            if len(bullet) > 15:  # Min 15 chars
                cleaned_bullets.append(bullet)
        
        return cleaned_bullets
    
    def extract_action_verb(self, responsibility: str) -> str:
        """
        Extract primary action verb from responsibility
        
        Args:
            responsibility: Single responsibility statement
            
        Returns:
            Primary action verb or empty string
        """
        resp_lower = responsibility.lower()
        
        # Check each category
        for category, verbs in self.action_verbs.items():
            for verb in verbs:
                if verb in resp_lower:
                    return verb
        
        # If not found, extract first verb (word ending in common verb suffixes)
        words = resp_lower.split()
        for word in words[:5]:  # Check first 5 words
            if len(word) > 3 and (word.endswith('ing') or word.endswith('kan') or word.endswith('i')):
                return word
        
        return ""
    
    def categorize_action(self, verb: str) -> str:
        """
        Categorize action verb
        
        Args:
            verb: Action verb
            
        Returns:
            Category name
        """
        verb_lower = verb.lower()
        
        for category, verbs in self.action_verbs.items():
            if verb_lower in verbs:
                return category
        
        return "other"
    
    def categorize_responsibility(self, responsibility: str) -> str:
        """
        Categorize entire responsibility statement
        
        Args:
            responsibility: Responsibility text
            
        Returns:
            Category name
        """
        resp_lower = responsibility.lower()
        
        # Score each category
        scores = {}
        for category, keywords in self.resp_categories.items():
            score = sum(1 for keyword in keywords if keyword in resp_lower)
            if score > 0:
                scores[category] = score
        
        # Return highest scoring category
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "general"
    
    def detect_seniority_indicators(self, responsibilities: List[str]) -> Dict[str, int]:
        """
        Detect seniority level from responsibilities
        
        Args:
            responsibilities: List of responsibility statements
            
        Returns:
            Dictionary with seniority indicators
        """
        indicators = {
            'leadership': 0,
            'management': 0,
            'technical': 0,
            'strategic': 0,
        }
        
        leadership_keywords = ['lead', 'manage', 'mentor', 'supervise', 'team', 'memimpin', 'mengelola']
        management_keywords = ['budget', 'plan', 'strategy', 'roadmap', 'anggaran', 'strategi']
        technical_keywords = ['code', 'develop', 'implement', 'build', 'programming', 'mengembangkan']
        strategic_keywords = ['strategy', 'vision', 'direction', 'objectives', 'strategi', 'visi']
        
        all_text = ' '.join(responsibilities).lower()
        
        indicators['leadership'] = sum(1 for kw in leadership_keywords if kw in all_text)
        indicators['management'] = sum(1 for kw in management_keywords if kw in all_text)
        indicators['technical'] = sum(1 for kw in technical_keywords if kw in all_text)
        indicators['strategic'] = sum(1 for kw in strategic_keywords if kw in all_text)
        
        return indicators
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize responsibilities text
        
        Args:
            text: Responsibilities text
            
        Returns:
            Dictionary with parsed responsibilities
        """
        if not self.validate_input(text):
            return {
                'responsibilities': [],
                'count': 0,
                'categorized': {},
                'action_verbs': [],
                'original': text,
                'error': 'Invalid input'
            }
        
        # Parse bullet points
        bullets = self.parse_bullet_points(text)
        
        # Analyze each responsibility
        resp_data = []
        action_verbs = []
        categorized = {}
        
        for bullet in bullets:
            # Extract action verb
            action = self.extract_action_verb(bullet)
            action_category = self.categorize_action(action) if action else "other"
            
            # Categorize responsibility
            category = self.categorize_responsibility(bullet)
            
            # Build data
            resp_info = {
                'text': bullet,
                'action_verb': action,
                'action_category': action_category,
                'category': category,
                'length': len(bullet)
            }
            resp_data.append(resp_info)
            
            if action:
                action_verbs.append(action)
            
            # Group by category
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(bullet)
        
        # Detect seniority
        seniority = self.detect_seniority_indicators(bullets)
        
        # Build result
        result = {
            'responsibilities': resp_data,
            'count': len(resp_data),
            'categorized': categorized,
            'action_verbs': list(set(action_verbs)),  # Unique verbs
            'seniority_indicators': seniority,
            'original': text[:200] + '...' if len(text) > 200 else text,
            'metadata': {
                'has_leadership': seniority['leadership'] > 0,
                'has_management': seniority['management'] > 0,
                'is_technical': seniority['technical'] > 2,
                'categories': list(categorized.keys())
            }
        }
        
        return result


if __name__ == "__main__":
    # Test
    tokenizer = ResponsibilityTokenizer()
    
    test_text = """
    • Mengembangkan dan maintain aplikasi web menggunakan React dan Node.js
    • Melakukan code review dan memberikan feedback kepada junior developer
    • Berkolaborasi dengan tim design dan product untuk implementasi fitur baru
    • Memastikan aplikasi memenuhi standar kualitas dan performance
    • Mentoring junior developers dalam best practices
    """
    
    result = tokenizer.tokenize(test_text)
    
    print("=" * 70)
    print("RESPONSIBILITY TOKENIZER TEST")
    print("=" * 70)
    print()
    print(f"Total responsibilities: {result['count']}")
    print(f"Action verbs: {result['action_verbs']}")
    print(f"Categories: {list(result['categorized'].keys())}")
    print(f"\nSeniority indicators:")
    for key, value in result['seniority_indicators'].items():
        print(f"  {key}: {value}")
    print()
    print("Parsed responsibilities:")
    for i, resp in enumerate(result['responsibilities'][:3], 1):
        print(f"{i}. {resp['text'][:60]}...")
        print(f"   Action: {resp['action_verb']} ({resp['action_category']})")
        print(f"   Category: {resp['category']}")
