# Location: backend/app/models/__init__.py (ADD THESE IMPORTS)
"""
Add these imports to existing __init__.py
"""

# Existing imports...
# from .job import Job
# from .job_listing import JobListing
# ... etc

# ADD: Module #5 - Skill Validation System
from .skill_category import SkillCategory
from .skill_dictionary import SkillsDictionary
from .skill_alias import SkillAlias
from .validation_queue import ValidationQueue
from .validation_history import ValidationHistory

__all__ = [
    # ... existing exports
    # "Job",
    # "JobListing",
    
    # Module #5
    "SkillCategory",
    "SkillsDictionary",
    "SkillAlias",
    "ValidationQueue",
    "ValidationHistory",
]