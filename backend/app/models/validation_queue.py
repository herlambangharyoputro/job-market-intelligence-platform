# Location: backend/app/models/validation_queue.py
"""
Validation Queue Model
Module #5: Skill Validation System

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, JSON
from datetime import datetime
from app.database.base import Base


class ValidationQueue(Base):
    """Queue of skills awaiting validation"""
    
    __tablename__ = 'validation_queue'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    skill_name = Column(String(100), nullable=False, index=True)
    source_count = Column(Integer, default=1)
    priority = Column(Integer, default=0, index=True)
    
    # Status
    status = Column(
        Enum('pending', 'in_progress', 'completed', 'skipped', name='queue_status_enum'),
        default='pending',
        index=True
    )
    assigned_to = Column(String(100), index=True)
    
    # Suggestions
    suggested_category_id = Column(Integer)
    confidence_score = Column(Numeric(3, 2))
    
    # Context
    context_sample = Column(JSON)
    queue_metadata = Column('metadata', JSON)  # Renamed to avoid SQLAlchemy reserved name
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ValidationQueue(id={self.id}, skill='{self.skill_name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'source_count': self.source_count,
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'suggested_category_id': self.suggested_category_id,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'context_sample': self.context_sample,
            'metadata': self.queue_metadata,  # Return as 'metadata' in API response
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }