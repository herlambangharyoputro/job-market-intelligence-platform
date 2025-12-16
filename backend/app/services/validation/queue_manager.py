# Location: backend/app/services/validation/queue_manager.py
"""
Validation Queue Manager Service
Module #5: Skill Validation System

Manages validation queue operations, prioritization, and filtering

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from app.models.validation_queue import ValidationQueue
from app.models.skill_category import SkillCategory


class QueueManagerService:
    """Service for managing validation queue"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
    
    def get_queue_items(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_priority: Optional[int] = None,
        sort_by: str = 'priority',
        sort_order: str = 'desc'
    ) -> Tuple[List[ValidationQueue], int]:
        """
        Get queue items with filtering and pagination
        """
        
        # Build query
        query = self.db.query(ValidationQueue)
        
        # Apply filters
        if status:
            query = query.filter(ValidationQueue.status == status)
        
        if search:
            query = query.filter(
                ValidationQueue.skill_name.ilike(f"%{search}%")
            )
        
        if category_id:
            query = query.filter(
                ValidationQueue.suggested_category_id == category_id
            )
        
        if min_priority is not None:
            query = query.filter(ValidationQueue.priority >= min_priority)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if sort_by == 'priority':
            order_col = ValidationQueue.priority
        elif sort_by == 'count':
            order_col = ValidationQueue.source_count
        elif sort_by == 'created':
            order_col = ValidationQueue.created_at
        else:
            order_col = ValidationQueue.priority
        
        if sort_order == 'desc':
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
        
        # Apply pagination
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    def get_queue_item(self, queue_id: int) -> Optional[ValidationQueue]:
        """Get single queue item by ID"""
        
        return self.db.query(ValidationQueue).filter(
            ValidationQueue.id == queue_id
        ).first()
    
    def get_next_item(
        self,
        assigned_to: Optional[str] = None
    ) -> Optional[ValidationQueue]:
        """
        Get next item to review (highest priority, pending status)
        """
        
        query = self.db.query(ValidationQueue).filter(
            ValidationQueue.status == 'pending'
        ).order_by(
            ValidationQueue.priority.desc(),
            ValidationQueue.source_count.desc()
        )
        
        if assigned_to:
            # Check if user has items in progress
            in_progress = query.filter(
                ValidationQueue.status == 'in_progress',
                ValidationQueue.assigned_to == assigned_to
            ).first()
            
            if in_progress:
                return in_progress
        
        # Get next pending item
        next_item = query.first()
        
        if next_item and assigned_to:
            next_item.status = 'in_progress'
            next_item.assigned_to = assigned_to
            next_item.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(next_item)
        
        return next_item
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics
        """
        
        total = self.db.query(func.count(ValidationQueue.id)).scalar()
        
        # By status
        pending = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.status == 'pending'
        ).scalar()
        
        in_progress = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.status == 'in_progress'
        ).scalar()
        
        completed = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.status == 'completed'
        ).scalar()
        
        skipped = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.status == 'skipped'
        ).scalar()
        
        # High priority items
        high_priority = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.priority >= 50,
            ValidationQueue.status == 'pending'
        ).scalar()
        
        return {
            'total': total or 0,
            'pending': pending or 0,
            'in_progress': in_progress or 0,
            'completed': completed or 0,
            'skipped': skipped or 0,
            'high_priority': high_priority or 0,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2)
        }
    
    def reset_stuck_items(self, hours: int = 24) -> int:
        """
        Reset items stuck in 'in_progress' status
        """
        
        from datetime import timedelta
        threshold = datetime.now() - timedelta(hours=hours)
        
        stuck_items = self.db.query(ValidationQueue).filter(
            ValidationQueue.status == 'in_progress',
            ValidationQueue.updated_at < threshold
        ).all()
        
        count = 0
        for item in stuck_items:
            item.status = 'pending'
            item.assigned_to = None
            item.updated_at = datetime.now()
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def reprioritize_queue(self) -> int:
        """
        Recalculate priority based on source_count
        """
        
        items = self.db.query(ValidationQueue).filter(
            ValidationQueue.status == 'pending'
        ).all()
        
        count = 0
        for item in items:
            new_priority = min(item.source_count, 100)
            if new_priority != item.priority:
                item.priority = new_priority
                item.updated_at = datetime.now()
                count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def add_to_queue(
        self,
        skill_name: str,
        source_count: int = 1,
        priority: int = 0,
        suggested_category_id: Optional[int] = None,
        context_sample: Optional[List[Dict[str, Any]]] = None
    ) -> ValidationQueue:
        """
        Add new item to queue
        """
        
        # Check if already exists
        existing = self.db.query(ValidationQueue).filter(
            ValidationQueue.skill_name == skill_name
        ).first()
        
        if existing:
            # Update count
            existing.source_count += source_count
            existing.priority = min(existing.source_count, 100)
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # Create new
        queue_item = ValidationQueue(
            skill_name=skill_name,
            source_count=source_count,
            priority=priority or min(source_count, 100),
            status='pending',
            suggested_category_id=suggested_category_id,
            context_sample=context_sample
        )
        
        self.db.add(queue_item)
        self.db.commit()
        self.db.refresh(queue_item)
        
        return queue_item
    
    def bulk_update_status(
        self,
        queue_ids: List[int],
        new_status: str
    ) -> int:
        """
        Update status for multiple items
        """
        
        items = self.db.query(ValidationQueue).filter(
            ValidationQueue.id.in_(queue_ids)
        ).all()
        
        count = 0
        for item in items:
            item.status = new_status
            item.updated_at = datetime.now()
            if new_status == 'completed':
                item.completed_at = datetime.now()
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count