"""
Skill Tokenizer
Extracts and categorizes skills from text

Features:
- Parse comma/semicolon/newline separated skills
- Categorize skills (programming, framework, tool, soft skill)
- Normalize skill variations
- Remove duplicates

Usage:
    from app.services.preprocessing.tokenizers.skill_tokenizer import SkillTokenizer
    
    tokenizer = SkillTokenizer()
    result = tokenizer.tokenize("Python, Java, React, Communication, Teamwork")
"""

import re
from typing import Dict, Any, List, Set
from app.services.preprocessing.tokenizers.base_tokenizer import BaseTokenizer


class SkillTokenizer(BaseTokenizer):
    """Tokenize and categorize skills"""
    
    def __init__(self):
        super().__init__(use_cleaner=True, use_indonesian_nlp=True, lowercase=True)
        
        # Skill categories
        self.skill_categories = self._load_skill_categories()
        
        # Skill variations/aliases
        self.skill_aliases = self._load_skill_aliases()
    
    def _load_skill_categories(self) -> Dict[str, Set[str]]:
        """Load skill categories"""
        return {
            'programming_language': {
                'python', 'java', 'javascript', 'typescript', 'php', 'ruby',
                'c', 'c++', 'c#', 'go', 'golang', 'rust', 'swift', 'kotlin',
                'scala', 'perl', 'r', 'matlab', 'dart', 'elixir',
            },
            'frontend': {
                'html', 'css', 'react', 'reactjs', 'vue', 'vuejs', 'angular',
                'angularjs', 'svelte', 'next.js', 'nextjs', 'nuxt', 'nuxtjs',
                'jquery', 'bootstrap', 'tailwind', 'sass', 'less', 'webpack',
            },
            'backend': {
                'node.js', 'nodejs', 'express', 'expressjs', 'django', 'flask',
                'laravel', 'symfony', 'spring', 'spring boot', 'fastapi',
                'nest.js', 'nestjs', 'rails', 'ruby on rails', '.net', 'asp.net',
            },
            'database': {
                'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
                'oracle', 'sql server', 'sqlite', 'cassandra', 'elasticsearch',
                'mariadb', 'dynamodb', 'firebase', 'couchdb',
            },
            'devops': {
                'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab ci', 'github actions',
                'terraform', 'ansible', 'aws', 'azure', 'gcp', 'google cloud',
                'ci/cd', 'nginx', 'apache', 'linux', 'bash', 'shell',
            },
            'data_science': {
                'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow',
                'keras', 'pytorch', 'machine learning', 'ml', 'deep learning',
                'nlp', 'computer vision', 'data analysis', 'statistics',
            },
            'mobile': {
                'android', 'ios', 'react native', 'flutter', 'swift', 'kotlin',
                'xamarin', 'ionic', 'cordova',
            },
            'tools': {
                'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
                'slack', 'trello', 'postman', 'figma', 'sketch', 'photoshop',
                'illustrator', 'vscode', 'intellij', 'eclipse',
            },
            'testing': {
                'jest', 'mocha', 'chai', 'pytest', 'unittest', 'selenium',
                'cypress', 'junit', 'testng', 'qa', 'quality assurance',
            },
            'soft_skill': {
                'communication', 'komunikasi', 'teamwork', 'kerja sama tim',
                'leadership', 'kepemimpinan', 'problem solving', 'pemecahan masalah',
                'analytical', 'analitis', 'creative', 'kreatif', 'adaptable',
                'time management', 'manajemen waktu', 'presentation', 'presentasi',
                'negotiation', 'negosiasi', 'critical thinking', 'berpikir kritis',
            },
            'other': {
                'agile', 'scrum', 'kanban', 'rest api', 'graphql', 'microservices',
                'oauth', 'jwt', 'websocket', 'mvc', 'oop', 'design patterns',
            }
        }
    
    def _load_skill_aliases(self) -> Dict[str, str]:
        """Load skill aliases/variations"""
        return {
            # Programming languages
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'rb': 'ruby',
            
            # Frameworks
            'reactjs': 'react',
            'vuejs': 'vue',
            'angularjs': 'angular',
            'nextjs': 'next.js',
            'nuxtjs': 'nuxt',
            'expressjs': 'express',
            'nestjs': 'nest.js',
            
            # Databases
            'postgres': 'postgresql',
            'mongo': 'mongodb',
            'mssql': 'sql server',
            
            # DevOps
            'k8s': 'kubernetes',
            'docker compose': 'docker',
            
            # Tools
            'vs code': 'vscode',
            'visual studio code': 'vscode',
            'intellij idea': 'intellij',
            
            # Soft skills (Indonesian)
            'kerja sama': 'teamwork',
            'komunikasi': 'communication',
            'kepemimpinan': 'leadership',
        }
    
    def normalize_skill(self, skill: str) -> str:
        """
        Normalize skill name
        
        Args:
            skill: Skill name
            
        Returns:
            Normalized skill name
        """
        # Clean
        skill = skill.lower().strip()
        
        # Remove version numbers
        skill = re.sub(r'\s*\d+\.?\d*\s*', ' ', skill)
        
        # Remove special characters but keep dots and hyphens
        skill = re.sub(r'[^\w\s.-]', '', skill)
        
        # Normalize whitespace
        skill = ' '.join(skill.split())
        
        # Apply aliases
        if skill in self.skill_aliases:
            skill = self.skill_aliases[skill]
        
        return skill
    
    def categorize_skill(self, skill: str) -> str:
        """
        Categorize a skill
        
        Args:
            skill: Skill name (normalized)
            
        Returns:
            Category name
        """
        skill_lower = skill.lower()
        
        for category, skills in self.skill_categories.items():
            if skill_lower in skills:
                return category
        
        return 'uncategorized'
    
    def parse_skills(self, text: str) -> List[str]:
        """
        Parse skills from text (comma/semicolon/newline separated)
        
        Args:
            text: Skills text
            
        Returns:
            List of individual skills
        """
        if not text:
            return []
        
        # Split by common delimiters
        # Handle: comma, semicolon, newline, bullet points
        delimiters = r'[,;\n•·]'
        skills = re.split(delimiters, text)
        
        # Clean each skill
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill:
                cleaned_skills.append(skill)
        
        return cleaned_skills
    
    def extract_proficiency(self, skill_text: str) -> tuple:
        """
        Extract proficiency level if mentioned
        
        Args:
            skill_text: Skill text (may include proficiency)
            
        Returns:
            Tuple of (skill, proficiency)
        """
        proficiency_keywords = {
            'expert': ['expert', 'advanced', 'mahir', 'ahli'],
            'intermediate': ['intermediate', 'menengah', 'cukup'],
            'beginner': ['beginner', 'basic', 'pemula', 'dasar'],
        }
        
        skill_lower = skill_text.lower()
        
        for level, keywords in proficiency_keywords.items():
            for keyword in keywords:
                if keyword in skill_lower:
                    # Remove proficiency keyword from skill
                    clean_skill = skill_lower.replace(keyword, '').strip()
                    return (clean_skill, level)
        
        return (skill_text, None)
    
    def tokenize(self, text: str) -> Dict[str, Any]:
        """
        Tokenize skills text
        
        Args:
            text: Skills text (comma/semicolon/newline separated)
            
        Returns:
            Dictionary with extracted and categorized skills
        """
        if not self.validate_input(text):
            return {
                'skills': [],
                'categorized': {},
                'total_count': 0,
                'original': text,
                'error': 'Invalid input'
            }
        
        # Parse individual skills
        raw_skills = self.parse_skills(text)
        
        # Process each skill
        skills_data = []
        categorized = {}
        
        for raw_skill in raw_skills:
            # Extract proficiency
            skill, proficiency = self.extract_proficiency(raw_skill)
            
            # Normalize
            normalized = self.normalize_skill(skill)
            
            if not normalized:
                continue
            
            # Categorize
            category = self.categorize_skill(normalized)
            
            # Add to results
            skill_info = {
                'original': raw_skill,
                'normalized': normalized,
                'category': category,
                'proficiency': proficiency
            }
            skills_data.append(skill_info)
            
            # Group by category
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(normalized)
        
        # Remove duplicates within categories
        for category in categorized:
            categorized[category] = list(set(categorized[category]))
        
        # Build result
        result = {
            'skills': skills_data,
            'categorized': categorized,
            'total_count': len(skills_data),
            'unique_count': len(set([s['normalized'] for s in skills_data])),
            'categories': list(categorized.keys()),
            'original': text,
            'metadata': {
                'has_programming': 'programming_language' in categorized,
                'has_soft_skills': 'soft_skill' in categorized,
                'category_count': len(categorized)
            }
        }
        
        return result


if __name__ == "__main__":
    # Test examples
    tokenizer = SkillTokenizer()
    
    test_cases = [
        "Python, Java, JavaScript, React, MySQL",
        "Communication, Teamwork, Leadership, Problem Solving",
        "Python (expert), React.js, Node.js, MongoDB, Docker, Kubernetes",
        "HTML, CSS, JavaScript; React; Vue.js; Angular",
        "Data Analysis, Machine Learning, TensorFlow, Pandas, NumPy",
    ]
    
    print("=" * 70)
    print("SKILL TOKENIZER TEST")
    print("=" * 70)
    print()
    
    for test in test_cases:
        result = tokenizer.tokenize(test)
        
        print(f"Original: {result['original']}")
        print(f"Total: {result['total_count']} skills ({result['unique_count']} unique)")
        print(f"Categories: {result['categories']}")
        print("Categorized:")
        for category, skills in result['categorized'].items():
            print(f"  {category}: {skills}")
        print("-" * 70)
