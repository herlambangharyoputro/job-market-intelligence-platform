# Location: backend/app/services/validation/skill_validator.py
"""
Skill Validation Service
Module #5: Skill Validation System

Core validation logic for skills approval/rejection workflow

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.skill_dictionary import SkillsDictionary
from app.models.validation_queue import ValidationQueue
from app.models.validation_history import ValidationHistory
from app.models.skill_category import SkillCategory


class SkillValidatorService:
    """Service for validating skills"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
    
    def approve_skill(
        self,
        queue_item: ValidationQueue,
        category_id: Optional[int] = None,
        validator_user: str = "system",
        notes: Optional[str] = None
    ) -> SkillsDictionary:
        """
        Approve a skill from validation queue
        
        Creates entry in skills_dictionary, updates queue status,
        and logs to history
        """
        
        # Check if skill already exists in dictionary
        existing = self.db.query(SkillsDictionary).filter(
            SkillsDictionary.skill_name == queue_item.skill_name
        ).first()
        
        if existing:
            # Update existing
            existing.is_validated = True
            existing.validation_status = 'approved'
            if category_id:
                old_category = existing.category_id
                existing.category_id = category_id
            existing.usage_count = queue_item.source_count
            existing.updated_at = datetime.now()
            
            skill = existing
        else:
            # Create new
            skill = SkillsDictionary(
                skill_name=queue_item.skill_name,
                normalized_name=queue_item.skill_name.lower().strip(),
                category_id=category_id or queue_item.suggested_category_id,
                is_validated=True,
                is_active=True,
                validation_status='approved',
                confidence_score=queue_item.confidence_score,
                usage_count=queue_item.source_count
            )
            self.db.add(skill)
        
        # Update queue status
        queue_item.status = 'completed'
        queue_item.completed_at = datetime.now()
        queue_item.updated_at = datetime.now()
        
        # Flush to get skill.id
        self.db.flush()
        
        # Log to history
        history = ValidationHistory(
            skill_id=skill.id,
            validator_user=validator_user,
            action='approved',
            old_category_id=None,
            new_category_id=category_id,
            old_status='pending',
            new_status='approved',
            notes=notes,
            metadata={
                'queue_id': queue_item.id,
                'source_count': queue_item.source_count
            }
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(skill)
        
        return skill
    
    def reject_skill(
        self,
        queue_item: ValidationQueue,
        validator_user: str = "system",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reject a skill from validation queue
        
        Marks as rejected, updates queue, logs to history
        """
        
        # Check if exists in dictionary
        existing = self.db.query(SkillsDictionary).filter(
            SkillsDictionary.skill_name == queue_item.skill_name
        ).first()
        
        if existing:
            # Update to rejected
            skill_id = existing.id
            existing.is_validated = True
            existing.is_active = False
            existing.validation_status = 'rejected'
            existing.updated_at = datetime.now()
        else:
            # Create as rejected
            skill = SkillsDictionary(
                skill_name=queue_item.skill_name,
                normalized_name=queue_item.skill_name.lower().strip(),
                is_validated=True,
                is_active=False,
                validation_status='rejected'
            )
            self.db.add(skill)
            self.db.flush()
            skill_id = skill.id
        
        # Update queue
        queue_item.status = 'completed'
        queue_item.completed_at = datetime.now()
        queue_item.updated_at = datetime.now()
        
        # Log to history
        history = ValidationHistory(
            skill_id=skill_id,
            validator_user=validator_user,
            action='rejected',
            old_status='pending',
            new_status='rejected',
            notes=notes,
            metadata={'queue_id': queue_item.id}
        )
        self.db.add(history)
        
        self.db.commit()
        
        return {
            'skill_id': skill_id,
            'skill_name': queue_item.skill_name,
            'status': 'rejected'
        }
    
    def skip_skill(
        self,
        queue_item: ValidationQueue,
        validator_user: str = "system"
    ) -> Dict[str, Any]:
        """
        Skip a skill for later review
        """
        
        queue_item.status = 'skipped'
        queue_item.updated_at = datetime.now()
        
        self.db.commit()
        
        return {
            'queue_id': queue_item.id,
            'skill_name': queue_item.skill_name,
            'status': 'skipped'
        }
    
    def bulk_validate(
        self,
        queue_ids: List[int],
        action: str,
        category_id: Optional[int] = None,
        validator_user: str = "system"
    ) -> Dict[str, Any]:
        """
        Validate multiple skills at once
        """
        
        results = {
            'total': len(queue_ids),
            'succeeded': 0,
            'failed': 0,
            'details': []
        }
        
        for queue_id in queue_ids:
            try:
                queue_item = self.db.query(ValidationQueue).filter(
                    ValidationQueue.id == queue_id
                ).first()
                
                if not queue_item:
                    results['failed'] += 1
                    results['details'].append({
                        'queue_id': queue_id,
                        'success': False,
                        'error': 'Queue item not found'
                    })
                    continue
                
                if action == 'approve':
                    skill = self.approve_skill(
                        queue_item,
                        category_id=category_id,
                        validator_user=validator_user
                    )
                    results['succeeded'] += 1
                    results['details'].append({
                        'queue_id': queue_id,
                        'skill_id': skill.id,
                        'skill_name': skill.skill_name,
                        'success': True
                    })
                
                elif action == 'reject':
                    result = self.reject_skill(
                        queue_item,
                        validator_user=validator_user
                    )
                    results['succeeded'] += 1
                    results['details'].append({
                        'queue_id': queue_id,
                        'success': True,
                        **result
                    })
                
                elif action == 'skip':
                    result = self.skip_skill(queue_item, validator_user)
                    results['succeeded'] += 1
                    results['details'].append({
                        'queue_id': queue_id,
                        'success': True,
                        **result
                    })
            
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'queue_id': queue_id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics for dashboard
        """
        
        # Dictionary stats
        total_skills = self.db.query(func.count(SkillsDictionary.id)).scalar()
        validated = self.db.query(func.count(SkillsDictionary.id)).filter(
            SkillsDictionary.is_validated == True
        ).scalar()
        pending = self.db.query(func.count(SkillsDictionary.id)).filter(
            SkillsDictionary.validation_status == 'pending'
        ).scalar()
        rejected = self.db.query(func.count(SkillsDictionary.id)).filter(
            SkillsDictionary.validation_status == 'rejected'
        ).scalar()
        
        # Queue stats
        total_queue = self.db.query(func.count(ValidationQueue.id)).scalar()
        queue_pending = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.status == 'pending'
        ).scalar()
        queue_completed = self.db.query(func.count(ValidationQueue.id)).filter(
            ValidationQueue.status == 'completed'
        ).scalar()
        
        # Category stats
        total_categories = self.db.query(func.count(SkillCategory.id)).scalar()
        active_categories = self.db.query(func.count(SkillCategory.id)).filter(
            SkillCategory.is_active == True
        ).scalar()
        
        # Recent activity
        recent_history = self.db.query(ValidationHistory).order_by(
            ValidationHistory.created_at.desc()
        ).limit(10).all()
        
        # Calculate validation rate
        validation_rate = (validated / total_skills * 100) if total_skills > 0 else 0
        
        return {
            'total_skills': total_skills or 0,
            'validated': validated or 0,
            'pending': pending or 0,
            'rejected': rejected or 0,
            'validation_rate': round(validation_rate, 2),
            'total_queue_items': total_queue or 0,
            'queue_pending': queue_pending or 0,
            'queue_completed': queue_completed or 0,
            'total_categories': total_categories or 0,
            'active_categories': active_categories or 0,
            'recent_activity': [h.to_dict() for h in recent_history]
        }
    
    def update_skill_category(
        self,
        skill_id: int,
        new_category_id: int,
        validator_user: str = "system",
        notes: Optional[str] = None
    ) -> SkillsDictionary:
        """
        Update skill category
        """
        
        skill = self.db.query(SkillsDictionary).filter(
            SkillsDictionary.id == skill_id
        ).first()
        
        if not skill:
            raise ValueError(f"Skill {skill_id} not found")
        
        old_category = skill.category_id
        skill.category_id = new_category_id
        skill.updated_at = datetime.now()
        
        # Log to history
        history = ValidationHistory(
            skill_id=skill_id,
            validator_user=validator_user,
            action='updated',
            old_category_id=old_category,
            new_category_id=new_category_id,
            notes=notes
        )
        self.db.add(history)
        
        self.db.commit()
        self.db.refresh(skill)
        
        return skill