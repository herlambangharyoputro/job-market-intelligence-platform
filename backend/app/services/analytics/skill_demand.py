# Location: backend/app/services/analytics/skill_demand.py
"""
Skills Demand Analysis Service - UPDATED for actual token format
Module #4: Skills Demand Analysis

UPDATED: Now handles the actual token structure:
{
  "skills": {
    "count": 5,
    "top": ["skill1", "skill2", ...],
    "categories": ["category1", ...]
  }
}

Author: Arya
Date: 2025-12-16 (Updated)
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import text, func


class SkillDemandService:
    """Service for analyzing skill demand from job market data"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
        self.skills_frequency = Counter()
        self.skills_by_category = defaultdict(Counter)
        self.skill_cooccurrence = defaultdict(int)
        self.jobs_analyzed = 0
        self.skills_total = 0
    
    def extract_skills_from_jobs(
        self,
        limit: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        location: Optional[str] = None,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract tokenized skills from database
        
        UPDATED: Handles actual token format with skills.top array
        """
        # Build query
        query = """
        SELECT 
            id,
            judul,
            perusahaan,
            lokasi,
            level,
            tokens,
            tanggal_posting,
            is_tokenized
        FROM jobs
        WHERE is_tokenized = TRUE
        AND tokens IS NOT NULL
        """
        
        params = {}
        
        # Add filters
        if date_from:
            query += " AND tanggal_posting >= :date_from"
            params['date_from'] = date_from
        
        if date_to:
            query += " AND tanggal_posting <= :date_to"
            params['date_to'] = date_to
        
        if location:
            query += " AND lokasi LIKE :location"
            params['location'] = f"%{location}%"
        
        if level:
            query += " AND level LIKE :level"
            params['level'] = f"%{level}%"
        
        # Add limit
        if limit:
            query += f" LIMIT {limit}"
        
        # Execute query
        result = self.db.execute(text(query), params)
        rows = result.fetchall()
        
        # Parse skills from tokens JSON
        jobs_with_skills = []
        
        for row in rows:
            job_data = {
                'id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'level': row[4],
                'posting_date': row[6],
                'skills': []
            }
            
            # Parse tokens JSON
            if row[5]:  # tokens column
                try:
                    tokens = json.loads(row[5]) if isinstance(row[5], str) else row[5]
                    
                    # ===== UPDATED: Handle actual token format =====
                    if 'skills' in tokens:
                        skills_data = tokens['skills']
                        
                        if isinstance(skills_data, dict):
                            # Format 1: {"top": [...], "categories": [...]}
                            if 'top' in skills_data:
                                top_skills = skills_data['top']
                                categories = skills_data.get('categories', [])
                                
                                # Convert to expected format
                                if isinstance(top_skills, list):
                                    for skill in top_skills:
                                        if skill:  # Skip empty strings
                                            # Try to match category
                                            category = 'uncategorized'
                                            if categories and len(categories) > 0:
                                                category = categories[0] if len(categories) == 1 else self._infer_category(skill)
                                            
                                            job_data['skills'].append({
                                                'normalized': skill.lower().strip(),
                                                'category': category
                                            })
                            
                            # Format 2: Old format with nested 'skills' key
                            elif 'skills' in skills_data:
                                skill_list = skills_data['skills']
                                if isinstance(skill_list, list):
                                    job_data['skills'] = skill_list
                            
                            # Format 3: Categorized format
                            elif 'categorized' in skills_data:
                                categorized = skills_data['categorized']
                                for category, skill_list in categorized.items():
                                    for skill in skill_list:
                                        job_data['skills'].append({
                                            'normalized': skill,
                                            'category': category
                                        })
                        
                        elif isinstance(skills_data, list):
                            # Direct list of skills
                            for skill in skills_data:
                                if isinstance(skill, str):
                                    job_data['skills'].append({
                                        'normalized': skill.lower().strip(),
                                        'category': 'uncategorized'
                                    })
                                elif isinstance(skill, dict):
                                    job_data['skills'].append(skill)
                    
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    # Skip jobs with invalid tokens
                    continue
            
            # Only include jobs with skills
            if job_data['skills']:
                jobs_with_skills.append(job_data)
        
        return jobs_with_skills
    
    def _infer_category(self, skill: str) -> str:
        """
        Infer category from skill name
        Basic categorization logic
        """
        skill_lower = skill.lower()
        
        # Programming languages
        prog_langs = ['python', 'java', 'javascript', 'php', 'c++', 'ruby', 'go', 'kotlin', 'swift']
        if any(lang in skill_lower for lang in prog_langs):
            return 'programming_language'
        
        # Frontend
        frontend = ['react', 'vue', 'angular', 'html', 'css', 'frontend']
        if any(fw in skill_lower for fw in frontend):
            return 'frontend'
        
        # Backend
        backend = ['django', 'flask', 'spring', 'node', 'express', 'backend']
        if any(fw in skill_lower for fw in backend):
            return 'backend'
        
        # Databases
        databases = ['mysql', 'postgresql', 'mongodb', 'redis', 'sql', 'database']
        if any(db in skill_lower for db in databases):
            return 'database'
        
        # DevOps
        devops = ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'devops', 'aws', 'azure', 'gcp']
        if any(tool in skill_lower for tool in devops):
            return 'devops'
        
        # Design tools
        design = ['photoshop', 'illustrator', 'figma', 'sketch', 'design']
        if any(tool in skill_lower for tool in design):
            return 'tools'
        
        # Soft skills
        soft = ['komunikasi', 'teamwork', 'leadership', 'komunikatif', 'organised']
        if any(s in skill_lower for s in soft):
            return 'soft_skill'
        
        return 'uncategorized'
    
    def analyze_frequency(
        self,
        jobs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze skill frequency across all jobs"""
        
        skill_counts = Counter()
        skill_categories = {}
        
        for job in jobs_data:
            # Use set to count each skill once per job
            job_skills = set()
            
            for skill_info in job['skills']:
                # Extract skill name and category
                if isinstance(skill_info, dict):
                    skill_name = skill_info.get('normalized', '')
                    skill_category = skill_info.get('category', 'uncategorized')
                elif isinstance(skill_info, str):
                    skill_name = skill_info
                    skill_category = 'uncategorized'
                else:
                    continue
                
                if skill_name:
                    skill_name = skill_name.lower().strip()
                    job_skills.add(skill_name)
                    skill_categories[skill_name] = skill_category
            
            # Count each skill once per job
            for skill in job_skills:
                skill_counts[skill] += 1
                category = skill_categories.get(skill, 'uncategorized')
                self.skills_by_category[category][skill] += 1
        
        # Store results
        self.skills_frequency = skill_counts
        self.jobs_analyzed = len(jobs_data)
        self.skills_total = len(skill_counts)
        
        # Format output
        frequency_list = [
            {
                'skill': skill,
                'demand_count': count,
                'category': skill_categories.get(skill, 'uncategorized'),
                'percentage': round(count / len(jobs_data) * 100, 2),
                'rank': rank
            }
            for rank, (skill, count) in enumerate(skill_counts.most_common(), 1)
        ]
        
        return {
            'total_jobs': len(jobs_data),
            'total_skills': len(skill_counts),
            'skills': frequency_list
        }
    
    def analyze_cooccurrence(
        self,
        jobs_data: List[Dict[str, Any]],
        min_support: int = 5
    ) -> Dict[str, Any]:
        """Analyze which skills appear together"""
        
        cooccurrence = defaultdict(int)
        
        for job in jobs_data:
            # Get unique skills in this job
            job_skills = set()
            for skill_info in job['skills']:
                if isinstance(skill_info, dict):
                    skill_name = skill_info.get('normalized', '')
                elif isinstance(skill_info, str):
                    skill_name = skill_info
                else:
                    continue
                
                if skill_name:
                    job_skills.add(skill_name.lower().strip())
            
            # Create pairs
            skills_list = sorted(list(job_skills))
            for i in range(len(skills_list)):
                for j in range(i + 1, len(skills_list)):
                    pair = (skills_list[i], skills_list[j])
                    cooccurrence[pair] += 1
        
        # Filter and format
        pairs_list = []
        for pair, count in cooccurrence.items():
            if count >= min_support:
                # Calculate lift score
                skill1_freq = self.skills_frequency.get(pair[0], 1)
                skill2_freq = self.skills_frequency.get(pair[1], 1)
                
                expected = (skill1_freq * skill2_freq) / self.jobs_analyzed
                lift = count / expected if expected > 0 else 0
                
                pairs_list.append({
                    'skill_1': pair[0],
                    'skill_2': pair[1],
                    'cooccurrence_count': count,
                    'lift': round(lift, 3),
                    'confidence': round(count / skill1_freq, 3)
                })
        
        # Sort by co-occurrence count
        pairs_list.sort(key=lambda x: x['cooccurrence_count'], reverse=True)
        
        self.skill_cooccurrence = cooccurrence
        
        return {
            'total_pairs': len(pairs_list),
            'min_support': min_support,
            'pairs': pairs_list
        }
    
    def get_top_skills(
        self,
        n: int = 50,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get top N demanded skills"""
        
        if category and category in self.skills_by_category:
            skills_counter = self.skills_by_category[category]
        else:
            skills_counter = self.skills_frequency
        
        top_skills = [
            {
                'skill': skill,
                'demand_count': count,
                'percentage': round(count / self.jobs_analyzed * 100, 2),
                'rank': rank
            }
            for rank, (skill, count) in enumerate(skills_counter.most_common(n), 1)
        ]
        
        return top_skills
    
    def get_category_distribution(self) -> Dict[str, Any]:
        """Get distribution of skills across categories"""
        
        category_stats = []
        
        for category, skills_counter in self.skills_by_category.items():
            total_skills = len(skills_counter)
            total_demand = sum(skills_counter.values())
            
            category_stats.append({
                'category': category,
                'unique_skills': total_skills,
                'total_demand': total_demand,
                'percentage': round(total_demand / self.jobs_analyzed * 100, 2) if self.jobs_analyzed > 0 else 0,
                'avg_demand_per_skill': round(total_demand / total_skills, 2) if total_skills > 0 else 0
            })
        
        # Sort by total demand
        category_stats.sort(key=lambda x: x['total_demand'], reverse=True)
        
        return {
            'total_categories': len(category_stats),
            'categories': category_stats
        }
    
    def analyze_trends(
        self,
        jobs_data: List[Dict[str, Any]],
        period: str = 'month'
    ) -> Dict[str, Any]:
        """Analyze skill demand trends over time"""
        
        # Group jobs by period
        periods = defaultdict(list)
        
        for job in jobs_data:
            posting_date = job.get('posting_date')
            if not posting_date:
                continue
            
            # Determine period key
            if period == 'day':
                period_key = posting_date.strftime('%Y-%m-%d')
            elif period == 'week':
                period_key = posting_date.strftime('%Y-W%W')
            else:  # month
                period_key = posting_date.strftime('%Y-%m')
            
            periods[period_key].append(job)
        
        # Analyze each period
        trends_data = []
        
        for period_key in sorted(periods.keys()):
            period_jobs = periods[period_key]
            
            # Get skills for this period
            period_skills = Counter()
            for job in period_jobs:
                for skill_info in job['skills']:
                    if isinstance(skill_info, dict):
                        skill_name = skill_info.get('normalized', '')
                    elif isinstance(skill_info, str):
                        skill_name = skill_info
                    else:
                        continue
                    
                    if skill_name:
                        period_skills[skill_name.lower().strip()] += 1
            
            trends_data.append({
                'period': period_key,
                'job_count': len(period_jobs),
                'unique_skills': len(period_skills),
                'top_skills': [
                    {'skill': skill, 'count': count}
                    for skill, count in period_skills.most_common(10)
                ]
            })
        
        return {
            'period_type': period,
            'periods': trends_data,
            'total_periods': len(trends_data)
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        
        top_3 = [skill for skill, _ in self.skills_frequency.most_common(3)]
        
        return {
            'total_jobs_analyzed': self.jobs_analyzed,
            'total_unique_skills': self.skills_total,
            'total_categories': len(self.skills_by_category),
            'avg_skills_per_job': round(
                sum(self.skills_frequency.values()) / self.jobs_analyzed, 2
            ) if self.jobs_analyzed > 0 else 0,
            'top_3_skills': top_3,
            'categories': list(self.skills_by_category.keys()),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def run_complete_analysis(
        self,
        limit: Optional[int] = None,
        top_n: int = 50,
        min_cooccurrence: int = 5,
        **filters
    ) -> Dict[str, Any]:
        """Run complete skills demand analysis"""
        
        # Extract data
        jobs_data = self.extract_skills_from_jobs(limit=limit, **filters)
        
        if not jobs_data:
            return {
                'error': 'No jobs with skills found',
                'jobs_analyzed': 0
            }
        
        # Run analyses
        frequency_results = self.analyze_frequency(jobs_data)
        cooccurrence_results = self.analyze_cooccurrence(
            jobs_data,
            min_support=min_cooccurrence
        )
        top_skills = self.get_top_skills(n=top_n)
        category_dist = self.get_category_distribution()
        summary = self.generate_summary()
        
        # Optional: trend analysis if date filter applied
        trends = None
        if filters.get('date_from') or filters.get('date_to'):
            trends = self.analyze_trends(jobs_data, period='month')
        
        return {
            'summary': summary,
            'frequency': frequency_results,
            'cooccurrence': cooccurrence_results,
            'top_skills': top_skills,
            'category_distribution': category_dist,
            'trends': trends,
            'filters_applied': filters
        }


# Helper functions for external use

def get_skills_demand_report(
    db: Session,
    limit: Optional[int] = None,
    **filters
) -> Dict[str, Any]:
    """Convenience function to get complete skills demand report"""
    service = SkillDemandService(db)
    return service.run_complete_analysis(limit=limit, **filters)


def get_top_skills_by_category(
    db: Session,
    category: str,
    n: int = 20
) -> List[Dict[str, Any]]:
    """Get top skills for a specific category"""
    service = SkillDemandService(db)
    jobs_data = service.extract_skills_from_jobs()
    service.analyze_frequency(jobs_data)
    
    return service.get_top_skills(n=n, category=category)