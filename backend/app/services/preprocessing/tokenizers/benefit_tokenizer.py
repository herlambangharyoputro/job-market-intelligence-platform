"""
Benefit Tokenizer
Extracts and categorizes job benefits

Features:
- Parse benefit items
- Categorize benefits (salary, insurance, leave, etc)
- Normalize benefit names
- Detect monetary benefits

Usage:
    from app.services.preprocessing.tokenizers.benefit_tokenizer import BenefitTokenizer
    
    tokenizer = BenefitTokenizer()
    result = tokenizer.tokenize(benefits_text)
"""

import re
from typing import Dict, Any, List
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer


class BenefitTokenizer(BaseTokenizer):
    """Tokenize job benefits"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=True)
        
        # Benefit categories
        self.benefit_categories = self._load_benefit_categories()
    
    def _load_benefit_categories(self) -> Dict[str, List[str]]:
        """Load benefit categories and keywords"""
        return {
            'compensation': [
                'gaji', 'salary', 'tunjangan', 'allowance', 'bonus', 'insentif', 'incentive',
                'komisi', 'commission', 'overtime', 'lembur', 'thr', 'rapel'
            ],
            'insurance': [
                'asuransi', 'insurance', 'bpjs', 'kesehatan', 'health', 'medical',
                'jiwa', 'life insurance', 'dental', 'gigi', 'vision', 'mata'
            ],
            'leave': [
                'cuti', 'leave', 'annual leave', 'tahunan', 'sick leave', 'sakit',
                'maternity', 'paternity', 'melahirkan', 'ayah', 'unpaid leave'
            ],
            'work_arrangement': [
                'remote', 'wfh', 'work from home', 'flexible', 'fleksibel',
                'hybrid', 'kerja dari rumah', 'flexible hours', 'jam fleksibel'
            ],
            'development': [
                'training', 'pelatihan', 'development', 'pengembangan', 'course', 'kursus',
                'certification', 'sertifikasi', 'workshop', 'seminar', 'conference', 'konferensi',
                'learning', 'pembelajaran', 'mentoring', 'coaching'
            ],
            'facilities': [
                'laptop', 'komputer', 'computer', 'phone', 'handphone', 'hp',
                'internet', 'wifi', 'parking', 'parkir', 'gym', 'fitness',
                'meal', 'makan', 'snack', 'coffee', 'kopi', 'pantry'
            ],
            'career': [
                'promosi', 'promotion', 'career path', 'jalur karir', 'career development',
                'jenjang karir', 'advancement', 'kenaikan jabatan'
            ],
            'social': [
                'gathering', 'outing', 'team building', 'event', 'acara', 'social',
                'komunitas', 'community', 'klub', 'club', 'activity', 'aktivitas'
            ],
            'other': [
                'allowance', 'reimbursement', 'relocation', 'relokasi',
                'daycare', 'childcare', 'penitipan anak', 'discount', 'diskon'
            ]
        }
    
    def parse_bullet_points(self, text: str) -> List[str]:
        """Parse benefit bullet points"""
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
        
        # Comma separated
        if not bullets:
            # Try comma separation
            items = text.split(',')
            bullets = [item.strip() for item in items if item.strip() and len(item.strip()) > 5]
        
        # Newline separated
        if not bullets:
            lines = text.split('\n')
            bullets = [line.strip() for line in lines if line.strip() and len(line.strip()) > 5]
        
        # Clean bullets
        cleaned = []
        for bullet in bullets:
            bullet = ' '.join(bullet.split())
            if len(bullet) > 3:
                cleaned.append(bullet)
        
        return cleaned
    
    def categorize_benefit(self, benefit: str) -> str:
        """
        Categorize benefit
        
        Args:
            benefit: Benefit text
            
        Returns:
            Category name
        """
        benefit_lower = benefit.lower()
        
        # Score each category
        scores = {}
        for category, keywords in self.benefit_categories.items():
            score = sum(1 for kw in keywords if kw in benefit_lower)
            if score > 0:
                scores[category] = score
        
        # Return highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return 'other'
    
    def is_monetary(self, benefit: str) -> bool:
        """
        Check if benefit is monetary
        
        Args:
            benefit: Benefit text
            
        Returns:
            True if monetary
        """
        benefit_lower = benefit.lower()
        
        monetary_keywords = [
            'gaji', 'salary', 'bonus', 'tunjangan', 'allowance',
            'komisi', 'insentif', 'rp', 'rupiah', 'juta', 'ribu'
        ]
        
        return any(kw in benefit_lower for kw in monetary_keywords)
    
    def normalize_benefit(self, benefit: str) -> str:
        """
        Normalize benefit name
        
        Args:
            benefit: Raw benefit text
            
        Returns:
            Normalized benefit
        """
        # Common normalizations
        normalizations = {
            'asuransi kesehatan': 'health insurance',
            'bpjs kesehatan': 'health insurance',
            'bpjs ketenagakerjaan': 'employment insurance',
            'cuti tahunan': 'annual leave',
            'thr': 'holiday allowance',
            'bonus tahunan': 'annual bonus',
            'wfh': 'work from home',
            'work from home': 'remote work',
        }
        
        benefit_lower = benefit.lower().strip()
        
        for key, value in normalizations.items():
            if key in benefit_lower:
                return value
        
        return benefit_lower
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize benefits text
        
        Args:
            text: Benefits text
            
        Returns:
            Dictionary with parsed benefits
        """
        if not self.validate_input(text):
            return {
                'benefits': [],
                'count': 0,
                'categorized': {},
                'monetary_benefits': [],
                'original': text,
                'error': 'Invalid input'
            }
        
        # Parse bullets
        bullets = self.parse_bullet_points(text)
        
        # Analyze each benefit
        benefit_data = []
        categorized = {}
        monetary_benefits = []
        
        for bullet in bullets:
            # Categorize
            category = self.categorize_benefit(bullet)
            is_monetary = self.is_monetary(bullet)
            normalized = self.normalize_benefit(bullet)
            
            # Build data
            benefit_info = {
                'text': bullet,
                'normalized': normalized,
                'category': category,
                'is_monetary': is_monetary
            }
            benefit_data.append(benefit_info)
            
            # Group by category
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(bullet)
            
            # Collect monetary
            if is_monetary:
                monetary_benefits.append(bullet)
        
        # Build result
        result = {
            'benefits': benefit_data,
            'count': len(benefit_data),
            'categorized': categorized,
            'monetary_benefits': monetary_benefits,
            'categories': list(categorized.keys()),
            'original': text[:200] + '...' if len(text) > 200 else text,
            'metadata': {
                'has_insurance': 'insurance' in categorized,
                'has_leave': 'leave' in categorized,
                'has_development': 'development' in categorized,
                'has_monetary': len(monetary_benefits) > 0,
                'category_count': len(categorized)
            }
        }
        
        return result


if __name__ == "__main__":
    # Test
    tokenizer = BenefitTokenizer()
    
    test_text = """
    • Gaji kompetitif
    • BPJS Kesehatan dan Ketenagakerjaan
    • Bonus tahunan
    • Cuti tahunan 12 hari
    • Flexible working hours
    • Training dan development program
    • Laptop dan peralatan kerja
    • Team building activities
    """
    
    result = tokenizer.tokenize(test_text)
    
    print("=" * 70)
    print("BENEFIT TOKENIZER TEST")
    print("=" * 70)
    print()
    print(f"Total benefits: {result['count']}")
    print(f"Categories: {result['categories']}")
    print(f"Monetary benefits: {len(result['monetary_benefits'])}")
    print()
    print("Categorized benefits:")
    for category, benefits in result['categorized'].items():
        print(f"\n{category.upper()}:")
        for benefit in benefits:
            print(f"  - {benefit}")
