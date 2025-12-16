# Location: backend/app/models/validation_history.py
"""
Validation History Model
Module #5: Skill Validation System

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from datetime import datetime
from app.database.base import Base


class ValidationHistory(Base):
    """Audit trail for skill validation actions"""
    
    __tablename__ = 'skill_validation_history'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    skill_id = Column(Integer, nullable=False, index=True)
    validator_user = Column(String(100), index=True)
    
    # Action
    action = Column(
        Enum('created', 'approved', 'rejected', 'updated', 'merged', 'deleted', name='validation_action_enum'),
        nullable=False,
        index=True
    )
    
    # Changes tracking
    old_category_id = Column(Integer)
    new_category_id = Column(Integer)
    old_status = Column(String(20))
    new_status = Column(String(20))
    
    # Additional info
    notes = Column(Text)
    history_metadata = Column('metadata', JSON)  # Renamed to avoid SQLAlchemy reserved name
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<ValidationHistory(id={self.id}, skill_id={self.skill_id}, action='{self.action}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'validator_user': self.validator_user,
            'action': self.action,
            'old_category_id': self.old_category_id,
            'new_category_id': self.new_category_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'notes': self.notes,
            'metadata': self.history_metadata,  # Return as 'metadata' in API response
            'created_at': self.created_at.isoformat() if self.created_at else None
        }