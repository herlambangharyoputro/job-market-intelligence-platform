# Location: backend/app/models/skill_alias.py
"""
Skill Alias Model
Module #5: Skill Validation System 

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from app.database.base import Base


class SkillAlias(Base):
    """Skill variations and synonyms"""
    
    __tablename__ = 'skill_aliases'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    skill_id = Column(Integer, nullable=False, index=True)
    alias = Column(String(100), unique=True, nullable=False, index=True)
    
    # Metadata
    language = Column(String(5), default='id')
    alias_type = Column(
        Enum('synonym', 'abbreviation', 'translation', 'variation', name='alias_type_enum'),
        default='synonym'
    )
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SkillAlias(id={self.id}, alias='{self.alias}', skill_id={self.skill_id})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'alias': self.alias,
            'language': self.language,
            'alias_type': self.alias_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }