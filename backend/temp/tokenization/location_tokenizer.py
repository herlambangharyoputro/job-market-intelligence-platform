"""
Location Tokenizer
Extracts and normalizes location information from Indonesian job postings

Features:
- Extract city and province
- Normalize location names
- Handle variations (Jakarta, DKI Jakarta, Jakarta Pusat)
- Detect remote/WFH

Usage:
    from app.services.preprocessing.tokenizers.location_tokenizer import LocationTokenizer
    
    tokenizer = LocationTokenizer()
    result = tokenizer.tokenize("Jakarta Selatan, DKI Jakarta")
"""

import re
from typing import Dict, Any, Optional, List
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer


class LocationTokenizer(BaseTokenizer):
    """Tokenize and normalize location information"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=True)
        
        # Load location data
        self.provinces = self._load_provinces()
        self.major_cities = self._load_major_cities()
        self.location_aliases = self._load_location_aliases()
    
    def _load_provinces(self) -> Dict[str, str]:
        """Load Indonesian provinces with aliases"""
        return {
            'aceh': 'Aceh',
            'sumatera utara': 'Sumatera Utara',
            'sumut': 'Sumatera Utara',
            'sumatera barat': 'Sumatera Barat',
            'sumbar': 'Sumatera Barat',
            'riau': 'Riau',
            'jambi': 'Jambi',
            'sumatera selatan': 'Sumatera Selatan',
            'sumsel': 'Sumatera Selatan',
            'bengkulu': 'Bengkulu',
            'lampung': 'Lampung',
            'kepulauan bangka belitung': 'Kepulauan Bangka Belitung',
            'babel': 'Kepulauan Bangka Belitung',
            'kepulauan riau': 'Kepulauan Riau',
            'kepri': 'Kepulauan Riau',
            'dki jakarta': 'DKI Jakarta',
            'jakarta': 'DKI Jakarta',
            'jawa barat': 'Jawa Barat',
            'jabar': 'Jawa Barat',
            'jawa tengah': 'Jawa Tengah',
            'jateng': 'Jawa Tengah',
            'di yogyakarta': 'DI Yogyakarta',
            'yogyakarta': 'DI Yogyakarta',
            'jogja': 'DI Yogyakarta',
            'jawa timur': 'Jawa Timur',
            'jatim': 'Jawa Timur',
            'banten': 'Banten',
            'bali': 'Bali',
            'nusa tenggara barat': 'Nusa Tenggara Barat',
            'ntb': 'Nusa Tenggara Barat',
            'nusa tenggara timur': 'Nusa Tenggara Timur',
            'ntt': 'Nusa Tenggara Timur',
            'kalimantan barat': 'Kalimantan Barat',
            'kalbar': 'Kalimantan Barat',
            'kalimantan tengah': 'Kalimantan Tengah',
            'kalteng': 'Kalimantan Tengah',
            'kalimantan selatan': 'Kalimantan Selatan',
            'kalsel': 'Kalimantan Selatan',
            'kalimantan timur': 'Kalimantan Timur',
            'kaltim': 'Kalimantan Timur',
            'kalimantan utara': 'Kalimantan Utara',
            'kaltara': 'Kalimantan Utara',
            'sulawesi utara': 'Sulawesi Utara',
            'sulut': 'Sulawesi Utara',
            'sulawesi tengah': 'Sulawesi Tengah',
            'sulteng': 'Sulawesi Tengah',
            'sulawesi selatan': 'Sulawesi Selatan',
            'sulsel': 'Sulawesi Selatan',
            'sulawesi tenggara': 'Sulawesi Tenggara',
            'sultra': 'Sulawesi Tenggara',
            'gorontalo': 'Gorontalo',
            'sulawesi barat': 'Sulawesi Barat',
            'sulbar': 'Sulawesi Barat',
            'maluku': 'Maluku',
            'maluku utara': 'Maluku Utara',
            'malut': 'Maluku Utara',
            'papua': 'Papua',
            'papua barat': 'Papua Barat',
        }
    
    def _load_major_cities(self) -> Dict[str, str]:
        """Load major Indonesian cities with their provinces"""
        return {
            'jakarta': 'DKI Jakarta',
            'jakarta pusat': 'DKI Jakarta',
            'jakarta utara': 'DKI Jakarta',
            'jakarta selatan': 'DKI Jakarta',
            'jakarta barat': 'DKI Jakarta',
            'jakarta timur': 'DKI Jakarta',
            'surabaya': 'Jawa Timur',
            'bandung': 'Jawa Barat',
            'bekasi': 'Jawa Barat',
            'medan': 'Sumatera Utara',
            'tangerang': 'Banten',
            'tangerang selatan': 'Banten',
            'depok': 'Jawa Barat',
            'semarang': 'Jawa Tengah',
            'palembang': 'Sumatera Selatan',
            'makassar': 'Sulawesi Selatan',
            'batam': 'Kepulauan Riau',
            'pekanbaru': 'Riau',
            'bogor': 'Jawa Barat',
            'malang': 'Jawa Timur',
            'yogyakarta': 'DI Yogyakarta',
            'jogja': 'DI Yogyakarta',
            'denpasar': 'Bali',
            'balikpapan': 'Kalimantan Timur',
            'samarinda': 'Kalimantan Timur',
            'banjarmasin': 'Kalimantan Selatan',
            'manado': 'Sulawesi Utara',
            'padang': 'Sumatera Barat',
            'pontianak': 'Kalimantan Barat',
            'cirebon': 'Jawa Barat',
            'solo': 'Jawa Tengah',
            'surakarta': 'Jawa Tengah',
        }
    
    def _load_location_aliases(self) -> Dict[str, str]:
        """Load common location aliases"""
        return {
            'jkt': 'jakarta',
            'sby': 'surabaya',
            'bdg': 'bandung',
            'jog': 'jogja',
            'mlg': 'malang',
            'smg': 'semarang',
        }
    
    def normalize_location(self, location: str) -> str:
        """
        Normalize location name
        
        Args:
            location: Raw location text
            
        Returns:
            Normalized location
        """
        if not location:
            return ""
        
        location = location.lower().strip()
        
        # Apply aliases
        if location in self.location_aliases:
            location = self.location_aliases[location]
        
        # Remove common prefixes
        location = re.sub(r'^(kota|kab\.|kabupaten)\s+', '', location)
        
        return location
    
    def extract_city(self, location: str) -> Optional[str]:
        """
        Extract city from location text
        
        Args:
            location: Location text
            
        Returns:
            City name
        """
        location_lower = self.normalize_location(location)
        
        # Check if it's a known city
        for city in self.major_cities.keys():
            if city in location_lower:
                return city.title()
        
        # If not found, extract first part (before comma)
        if ',' in location_lower:
            parts = location_lower.split(',')
            city = parts[0].strip()
            return city.title() if city else None
        
        # Return the whole text as city
        return location_lower.title()
    
    def extract_province(self, location: str) -> Optional[str]:
        """
        Extract province from location text
        
        Args:
            location: Location text
            
        Returns:
            Province name
        """
        location_lower = self.normalize_location(location)
        
        # Check if province is mentioned
        for prov_key, prov_name in self.provinces.items():
            if prov_key in location_lower:
                return prov_name
        
        # Try to infer from city
        city = self.extract_city(location)
        if city:
            city_lower = city.lower()
            if city_lower in self.major_cities:
                return self.major_cities[city_lower]
        
        return None
    
    def is_remote(self, location: str) -> bool:
        """
        Check if location indicates remote work
        
        Args:
            location: Location text
            
        Returns:
            True if remote
        """
        remote_keywords = [
            'remote', 'wfh', 'work from home', 'anywhere',
            'dari rumah', 'kerja dari rumah', 'flexible location',
            'seluruh indonesia', 'all indonesia'
        ]
        
        location_lower = location.lower()
        return any(keyword in location_lower for keyword in remote_keywords)
    
    def parse_location_detail(self, location: str) -> Dict[str, Any]:
        """
        Parse detailed location information
        
        Args:
            location: Location text
            
        Returns:
            Dictionary with location details
        """
        city = self.extract_city(location)
        province = self.extract_province(location)
        is_remote = self.is_remote(location)
        normalized = self.normalize_location(location)
        
        return {
            'city': city,
            'province': province,
            'is_remote': is_remote,
            'normalized': normalized,
            'full_location': f"{city}, {province}" if city and province else (city or province or normalized)
        }
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize location text
        
        Args:
            text: Location text
            
        Returns:
            Dictionary with location information
        """
        if not self.validate_input(text):
            return {
                'city': None,
                'province': None,
                'is_remote': False,
                'normalized': None,
                'original': text,
                'error': 'Invalid input'
            }
        
        # Parse location
        details = self.parse_location_detail(text)
        
        # Tokenize for search
        tokens = self.split_tokens(details['normalized'])
        
        result = {
            'city': details['city'],
            'province': details['province'],
            'is_remote': details['is_remote'],
            'normalized': details['normalized'],
            'full_location': details['full_location'],
            'tokens': tokens,
            'original': text,
            'metadata': {
                'has_city': details['city'] is not None,
                'has_province': details['province'] is not None,
                'is_complete': details['city'] is not None and details['province'] is not None
            }
        }
        
        return result


if __name__ == "__main__":
    # Test
    tokenizer = LocationTokenizer()
    
    test_locations = [
        "Jakarta Selatan, DKI Jakarta",
        "Surabaya",
        "Bandung, Jawa Barat",
        "Remote / Work From Home",
        "Yogyakarta",
        "Tangerang Selatan",
    ]
    
    print("=" * 70)
    print("LOCATION TOKENIZER TEST")
    print("=" * 70)
    print()
    
    for loc in test_locations:
        result = tokenizer.tokenize(loc)
        print(f"Original:  {result['original']}")
        print(f"City:      {result['city']}")
        print(f"Province:  {result['province']}")
        print(f"Remote:    {result['is_remote']}")
        print(f"Full:      {result['full_location']}")
        print("-" * 70)
