"""
Analytics Services Module
Location: backend/app/services/analytics/__init__.py

Provides various analytics services for job market intelligence
"""

from .skill_demand import (
    SkillDemandService,
    get_skills_demand_report,
    get_top_skills_by_category
)

__all__ = [
    'SkillDemandService',
    'get_skills_demand_report',
    'get_top_skills_by_category'
]