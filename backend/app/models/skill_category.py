# Location: backend/app/models/skill_category.py
"""
Skill Category Model
Module #5: Skill Validation System 

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class SkillCategory(Base):
    """Skill category taxonomy"""
    
    __tablename__ = 'skill_categories'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    category_name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100))
    description = Column(Text)
    
    # UI metadata
    icon = Column(String(50))
    color = Column(String(20))
    
    # Hierarchy
    parent_category_id = Column(Integer, index=True)
    
    # Organization
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<SkillCategory(id={self.id}, name='{self.category_name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'category_name': self.category_name,
            'display_name': self.display_name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'parent_category_id': self.parent_category_id,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }