"""
Indonesian NLP Module
Handles Indonesian-specific text processing for job postings

Features:
- Indonesian stopwords
- Slang normalization
- Stemming (using Sastrawi)
- Mixed ID-EN text handling

Usage:
    from app.services.preprocessing.indonesian_nlp import IndonesianNLP
    
    nlp = IndonesianNLP()
    tokens = nlp.tokenize("Kami mencari developer berpengalaman")
"""

import re
from typing import List, Optional, Set, Dict


class IndonesianNLP:
    """Indonesian language processing for job postings"""
    
    def __init__(self, use_stemming: bool = False, remove_stopwords: bool = False):
        """
        Initialize Indonesian NLP
        
        Args:
            use_stemming: Use Sastrawi stemmer
            remove_stopwords: Remove Indonesian stopwords
        """
        self.use_stemming = use_stemming
        self.remove_stopwords = remove_stopwords
        
        # Load stopwords
        self.stopwords = self._load_stopwords()
        
        # Load slang dictionary
        self.slang_dict = self._load_slang_dict()
        
        # Load job terms dictionary
        self.job_terms = self._load_job_terms()
        
        # Initialize stemmer if needed
        self.stemmer = None
        if use_stemming:
            self._init_stemmer()
    
    def _load_stopwords(self) -> Set[str]:
        """Load Indonesian stopwords"""
        stopwords = {
            # Common Indonesian stopwords
            'yang', 'untuk', 'pada', 'ke', 'para', 'namun', 'menurut', 'antara', 'oleh',
            'sehingga', 'saat', 'kami', 'kita', 'mereka', 'tersebut', 'ini', 'itu',
            'dari', 'dengan', 'di', 'dan', 'atau', 'adalah', 'sebagai', 'akan',
            'ada', 'juga', 'dapat', 'sudah', 'telah', 'harus', 'bisa', 'maka',
            
            # Job-specific stopwords (keep minimal)
            'lowongan', 'kerja', 'pekerjaan', 'posisi', 'dibutuhkan', 'dicari',
            
            # Common words (be careful not to remove too much)
            'saya', 'anda', 'dia', 'kami', 'kita', 'mereka',
        }
        
        return stopwords
    
    def _load_slang_dict(self) -> Dict[str, str]:
        """Load Indonesian slang/informal word mappings"""
        return {
            # Common abbreviations
            'yg': 'yang',
            'utk': 'untuk',
            'dgn': 'dengan',
            'dg': 'dengan',
            'tdk': 'tidak',
            'blm': 'belum',
            'sdh': 'sudah',
            'hrs': 'harus',
            'min': 'minimal',
            'maks': 'maksimal',
            'max': 'maksimal',
            'min.': 'minimal',
            'max.': 'maksimal',
            'thn': 'tahun',
            'bln': 'bulan',
            'hr': 'hari',
            'org': 'orang',
            'pt': 'perusahaan',
            'cv': 'curriculum vitae',
            'jln': 'jalan',
            'kel': 'kelurahan',
            'kec': 'kecamatan',
            'prov': 'provinsi',
            'no': 'nomor',
            'tel': 'telepon',
            'tlp': 'telepon',
            'hp': 'handphone',
            'dll': 'dan lain lain',
            'dsb': 'dan sebagainya',
            'dst': 'dan seterusnya',
            'dkk': 'dan kawan kawan',
            
            # Education
            's1': 'sarjana',
            's2': 'magister',
            's3': 'doktor',
            'd3': 'diploma tiga',
            'd4': 'diploma empat',
            'sma': 'sekolah menengah atas',
            'smk': 'sekolah menengah kejuruan',
            
            # Job terms
            'fulltime': 'full time',
            'parttime': 'part time',
            'freelance': 'lepas',
            'internship': 'magang',
        }
    
    def _load_job_terms(self) -> Dict[str, List[str]]:
        """Load job domain terminology"""
        return {
            # Technology terms (normalize variations)
            'fullstack': ['full stack', 'full-stack', 'fullstack'],
            'frontend': ['front end', 'front-end', 'frontend'],
            'backend': ['back end', 'back-end', 'backend'],
            'devops': ['dev ops', 'dev-ops', 'devops'],
            'database': ['data base', 'database', 'db'],
            'website': ['web site', 'website'],
            
            # Levels
            'junior': ['jr', 'junior', 'pemula'],
            'senior': ['sr', 'senior', 'berpengalaman'],
            'staff': ['staf', 'staff'],
            'manager': ['manajer', 'manager', 'mgr'],
            'supervisor': ['spv', 'supervisor'],
            'assistant': ['asst', 'assistant', 'asisten'],
        }
    
    def _init_stemmer(self):
        """Initialize Sastrawi stemmer"""
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
            factory = StemmerFactory()
            self.stemmer = factory.create_stemmer()
        except ImportError:
            print("Warning: Sastrawi not installed. Install with: pip install PySastrawi")
            self.stemmer = None
    
    def normalize_slang(self, text: str) -> str:
        """
        Normalize Indonesian slang and abbreviations
        
        Args:
            text: Text with potential slang
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        words = text.split()
        normalized = []
        
        for word in words:
            word_lower = word.lower()
            # Check if word is in slang dictionary
            if word_lower in self.slang_dict:
                normalized.append(self.slang_dict[word_lower])
            else:
                normalized.append(word)
        
        return ' '.join(normalized)
    
    def normalize_job_terms(self, text: str) -> str:
        """
        Normalize job-specific terms
        
        Args:
            text: Text with job terms
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        text_lower = text.lower()
        
        # Replace variations with standard form
        for standard, variations in self.job_terms.items():
            for variation in variations:
                text_lower = text_lower.replace(variation, standard)
        
        return text_lower
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize Indonesian text
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Normalize slang
        text = self.normalize_slang(text)
        
        # Basic tokenization (split by whitespace and punctuation)
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Remove stopwords if enabled
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.stopwords]
        
        # Stem if enabled
        if self.use_stemming and self.stemmer:
            tokens = [self.stemmer.stem(t) for t in tokens]
        
        return tokens
    
    def is_indonesian_word(self, word: str) -> bool:
        """
        Check if word is likely Indonesian (heuristic)
        
        Args:
            word: Word to check
            
        Returns:
            True if likely Indonesian
        """
        word_lower = word.lower()
        
        # Check if in stopwords
        if word_lower in self.stopwords:
            return True
        
        # Check if in slang dict
        if word_lower in self.slang_dict:
            return True
        
        # Check common Indonesian patterns
        indonesian_patterns = [
            r'.*[aiueo]{2}',  # Vowel pairs (common in Indonesian)
            r'ng\w+',          # 'ng' prefix
            r'\w+kan$',        # '-kan' suffix
            r'\w+an$',         # '-an' suffix
            r'me\w+',          # 'me-' prefix
            r'ber\w+',         # 'ber-' prefix
            r'per\w+',         # 'per-' prefix
        ]
        
        return any(re.match(pattern, word_lower) for pattern in indonesian_patterns)
    
    def separate_mixed_text(self, text: str) -> Dict[str, List[str]]:
        """
        Separate mixed Indonesian-English text
        
        Args:
            text: Mixed language text
            
        Returns:
            Dict with 'indonesian' and 'english' word lists
        """
        if not text:
            return {'indonesian': [], 'english': []}
        
        words = text.split()
        indonesian_words = []
        english_words = []
        
        for word in words:
            if self.is_indonesian_word(word):
                indonesian_words.append(word)
            else:
                english_words.append(word)
        
        return {
            'indonesian': indonesian_words,
            'english': english_words
        }


# Convenience functions
def normalize_indonesian_text(text: str) -> str:
    """
    Quick Indonesian text normalization
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    nlp = IndonesianNLP()
    text = nlp.normalize_slang(text)
    text = nlp.normalize_job_terms(text)
    return text


def tokenize_indonesian(text: str, remove_stopwords: bool = False) -> List[str]:
    """
    Quick Indonesian tokenization
    
    Args:
        text: Text to tokenize
        remove_stopwords: Remove stopwords
        
    Returns:
        List of tokens
    """
    nlp = IndonesianNLP(remove_stopwords=remove_stopwords)
    return nlp.tokenize(text)


if __name__ == "__main__":
    # Test examples
    nlp = IndonesianNLP(remove_stopwords=True)
    
    # Test slang normalization
    text1 = "Kami mencari developer yg berpengalaman min 2 thn"
    print(f"Original: {text1}")
    print(f"Normalized: {nlp.normalize_slang(text1)}")
    print()
    
    # Test tokenization
    text2 = "Dibutuhkan Full-Stack Developer untuk project website e-commerce"
    print(f"Original: {text2}")
    print(f"Tokens: {nlp.tokenize(text2)}")
    print()
    
    # Test mixed language
    text3 = "Mencari Frontend Developer yang menguasai React dan Vue.js"
    print(f"Original: {text3}")
    print(f"Separated: {nlp.separate_mixed_text(text3)}")
