# Location: backend/app/models/skill_dictionary.py
"""
Skills Dictionary Model
Module #5: Skill Validation System

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class SkillsDictionary(Base):
    """Master skills dictionary"""
    
    __tablename__ = 'skills_dictionary'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    skill_name = Column(String(100), unique=True, nullable=False, index=True)
    normalized_name = Column(String(100), nullable=False, index=True)
    
    # Categorization
    category_id = Column(Integer, index=True)
    subcategory = Column(String(50))
    
    # Validation
    is_validated = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True)
    validation_status = Column(
        Enum('pending', 'approved', 'rejected', name='validation_status_enum'),
        default='pending',
        index=True
    )
    confidence_score = Column(Numeric(3, 2))
    
    # Metadata
    usage_count = Column(Integer, default=0)
    description = Column(Text)
    skill_metadata = Column('metadata', JSON)  # Renamed to avoid SQLAlchemy reserved name
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<SkillsDictionary(id={self.id}, skill='{self.skill_name}', status='{self.validation_status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'normalized_name': self.normalized_name,
            'category_id': self.category_id,
            'subcategory': self.subcategory,
            'is_validated': self.is_validated,
            'is_active': self.is_active,
            'validation_status': self.validation_status,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'usage_count': self.usage_count,
            'description': self.description,
            'metadata': self.skill_metadata,  # Return as 'metadata' in API response
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }