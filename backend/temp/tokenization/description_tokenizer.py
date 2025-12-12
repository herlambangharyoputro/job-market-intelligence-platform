"""
Description Tokenizer
Processes job descriptions with sentence segmentation and keyword extraction

Features:
- Sentence segmentation
- Paragraph detection
- Keyword extraction
- Key phrase extraction
- Summary generation

Usage:
    from app.services.preprocessing.tokenizers.description_tokenizer import DescriptionTokenizer
    
    tokenizer = DescriptionTokenizer()
    result = tokenizer.tokenize(long_description_text)
"""

import re
from typing import Dict, Any, List, Optional
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer


class DescriptionTokenizer(BaseTokenizer):
    """Tokenize job descriptions"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=False)
        
        # Keywords to look for
        self.section_keywords = {
            'responsibilities': ['tanggung jawab', 'responsibilities', 'tugas', 'job description'],
            'requirements': ['persyaratan', 'requirements', 'kualifikasi', 'qualifications'],
            'benefits': ['benefit', 'tunjangan', 'fasilitas', 'keuntungan'],
            'company': ['tentang', 'about', 'company', 'perusahaan'],
        }
    
    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences
        
        Args:
            text: Description text
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # Split by sentence terminators
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter
        cleaned = []
        for sent in sentences:
            sent = sent.strip()
            if sent and len(sent) > 10:  # Min 10 chars
                cleaned.append(sent)
        
        return cleaned
    
    def detect_paragraphs(self, text: str) -> List[str]:
        """
        Detect paragraphs (double newline separated)
        
        Args:
            text: Description text
            
        Returns:
            List of paragraphs
        """
        if not text:
            return []
        
        # Split by double newline or multiple newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Clean
        cleaned = []
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 20:  # Min 20 chars
                cleaned.append(para)
        
        return cleaned
    
    def detect_sections(self, text: str) -> Dict[str, str]:
        """
        Detect different sections in description
        
        Args:
            text: Description text
            
        Returns:
            Dictionary of sections
        """
        sections = {}
        text_lower = text.lower()
        
        for section_name, keywords in self.section_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Try to extract section content
                    pattern = rf'{keyword}[\s:]*(.+?)(?=\n\n|\Z)'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        sections[section_name] = match.group(1).strip()
                        break
        
        return sections
    
    def extract_bullet_points(self, text: str) -> List[str]:
        """
        Extract bullet points from text
        
        Args:
            text: Description text
            
        Returns:
            List of bullet points
        """
        if not text:
            return []
        
        # Patterns for bullet points
        patterns = [
            r'[•·\-\*]\s*(.+)',  # Bullet symbols
            r'^\d+\.\s*(.+)',     # Numbered list
        ]
        
        bullets = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                bullet = match.group(1).strip()
                if bullet:
                    bullets.append(bullet)
        
        return bullets
    
    def extract_keywords_simple(self, text: str, top_n: int = 20) -> List[tuple]:
        """
        Extract keywords using simple frequency
        
        Args:
            text: Description text
            top_n: Number of top keywords
            
        Returns:
            List of (keyword, frequency) tuples
        """
        if not text:
            return []
        
        # Tokenize
        if self.use_indonesian_nlp:
            tokens = self.indo_nlp.tokenize(text)
        else:
            tokens = self.split_tokens(text.lower())
        
        # Filter short words
        tokens = [t for t in tokens if len(t) > 3]
        
        # Count frequency
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:top_n]
    
    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key phrases (bigrams/trigrams)
        
        Args:
            text: Description text
            top_n: Number of phrases
            
        Returns:
            List of key phrases
        """
        if not text:
            return []
        
        # Get sentences
        sentences = self.segment_sentences(text)
        
        phrases = []
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            # Extract noun phrases (simple: capitalized words together)
            caps_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence)
            phrases.extend(caps_phrases)
            
            # Extract common patterns
            # "pengalaman X tahun", "minimal X", etc
            patterns = [
                r'pengalaman\s+\d+\s+tahun',
                r'minimal\s+\w+',
                r'menguasai\s+\w+',
                r'\w+\s+developer',
                r'\w+\s+engineer',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                phrases.extend(matches)
        
        # Count and return top
        from collections import Counter
        phrase_counts = Counter(phrases)
        top_phrases = [phrase for phrase, count in phrase_counts.most_common(top_n)]
        
        return top_phrases
    
    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        Generate simple summary (first N sentences)
        
        Args:
            text: Description text
            max_sentences: Number of sentences for summary
            
        Returns:
            Summary text
        """
        sentences = self.segment_sentences(text)
        
        if not sentences:
            return ""
        
        # Take first N sentences
        summary_sentences = sentences[:max_sentences]
        summary = '. '.join(summary_sentences) + '.'
        
        return summary
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize job description
        
        Args:
            text: Job description text
            
        Returns:
            Dictionary with analysis results
        """
        if not self.validate_input(text):
            return {
                'sentences': [],
                'paragraphs': [],
                'keywords': [],
                'key_phrases': [],
                'summary': None,
                'sections': {},
                'bullet_points': [],
                'original': text,
                'error': 'Invalid input'
            }
        
        # Clean text
        cleaned = self.preprocess(text)
        
        # Analyze
        sentences = self.segment_sentences(cleaned)
        paragraphs = self.detect_paragraphs(text)  # Use original for paragraph detection
        sections = self.detect_sections(text)
        bullet_points = self.extract_bullet_points(text)
        keywords = self.extract_keywords_simple(cleaned, top_n=20)
        key_phrases = self.extract_key_phrases(text, top_n=10)
        summary = self.generate_summary(text, max_sentences=3)
        
        # Token count
        all_tokens = self.split_tokens(cleaned)
        
        result = {
            'sentences': sentences[:10],  # First 10 sentences
            'sentence_count': len(sentences),
            'paragraphs': paragraphs[:5],  # First 5 paragraphs
            'paragraph_count': len(paragraphs),
            'sections': sections,
            'bullet_points': bullet_points[:10],  # First 10 bullets
            'bullet_count': len(bullet_points),
            'keywords': [k for k, f in keywords[:20]],  # Top 20 keywords
            'keyword_freq': keywords[:20],
            'key_phrases': key_phrases,
            'summary': summary,
            'token_count': len(all_tokens),
            'char_count': len(cleaned),
            'original': text[:200] + '...' if len(text) > 200 else text,
            'metadata': {
                'has_sections': len(sections) > 0,
                'has_bullets': len(bullet_points) > 0,
                'is_structured': len(sections) > 0 or len(bullet_points) > 0,
            }
        }
        
        return result


if __name__ == "__main__":
    # Test
    tokenizer = DescriptionTokenizer()
    
    test_desc = """
    Kami mencari Full Stack Developer yang berpengalaman untuk bergabung dengan tim kami.
    
    Tanggung Jawab:
    • Mengembangkan aplikasi web menggunakan React dan Node.js
    • Melakukan code review dan testing
    • Berkolaborasi dengan tim design dan product
    
    Persyaratan:
    • Minimal 3 tahun pengalaman sebagai Full Stack Developer
    • Menguasai JavaScript, React, Node.js
    • Familiar dengan Git dan Agile methodology
    
    Benefit:
    • Gaji kompetitif
    • Asuransi kesehatan
    • Work from home flexibility
    """
    
    result = tokenizer.tokenize(test_desc)
    
    print("=" * 70)
    print("DESCRIPTION TOKENIZER TEST")
    print("=" * 70)
    print()
    print(f"Sentences: {result['sentence_count']}")
    print(f"Paragraphs: {result['paragraph_count']}")
    print(f"Sections: {list(result['sections'].keys())}")
    print(f"Bullet points: {result['bullet_count']}")
    print(f"Top keywords: {result['keywords'][:10]}")
    print(f"Key phrases: {result['key_phrases'][:5]}")
    print(f"\nSummary:\n{result['summary']}")
