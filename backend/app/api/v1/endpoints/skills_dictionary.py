# Location: backend/app/api/v1/endpoints/skills_dictionary.py
"""
Skills Dictionary API Endpoints
Module #5: Skill Validation System

CRUD operations for validated skills dictionary

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional

from app.database import get_db
from app.schemas.skill_dictionary import (
    SkillsDictionary,
    SkillsDictionaryCreate,
    SkillsDictionaryUpdate,
    SkillsDictionaryList,
    SkillsDictionaryWithCategory,
    ValidationStatus
)
from app.models.skill_dictionary import SkillsDictionary as SkillsDictionaryModel
from app.models.skill_category import SkillCategory
from app.services.validation.skill_validator import SkillValidatorService

router = APIRouter()


@router.get("/", response_model=SkillsDictionaryList)
async def get_skills_dictionary(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter by validation status"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by skill name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get skills dictionary with filtering
    
    Returns validated and categorized skills
    """
    
    try:
        # Build query
        query = db.query(SkillsDictionaryModel)
        
        # Apply filters
        if status:
            query = query.filter(SkillsDictionaryModel.validation_status == status)
        
        if category_id:
            query = query.filter(SkillsDictionaryModel.category_id == category_id)
        
        if search:
            query = query.filter(
                or_(
                    SkillsDictionaryModel.skill_name.ilike(f"%{search}%"),
                    SkillsDictionaryModel.normalized_name.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(SkillsDictionaryModel.is_active == is_active)
        
        # Get total
        total = query.count()
        
        # Get counts by status
        validated = db.query(func.count(SkillsDictionaryModel.id)).filter(
            SkillsDictionaryModel.is_validated == True
        ).scalar()
        
        pending = db.query(func.count(SkillsDictionaryModel.id)).filter(
            SkillsDictionaryModel.validation_status == 'pending'
        ).scalar()
        
        rejected = db.query(func.count(SkillsDictionaryModel.id)).filter(
            SkillsDictionaryModel.validation_status == 'rejected'
        ).scalar()
        
        # Get items
        items = query.order_by(
            SkillsDictionaryModel.usage_count.desc()
        ).offset(skip).limit(limit).all()
        
        return SkillsDictionaryList(
            total=total,
            validated=validated or 0,
            pending=pending or 0,
            rejected=rejected or 0,
            skills=[item.to_dict() for item in items]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get skills: {str(e)}"
        )


@router.get("/{skill_id}", response_model=SkillsDictionaryWithCategory)
async def get_skill(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single skill by ID with category details
    """
    
    skill = db.query(SkillsDictionaryModel).filter(
        SkillsDictionaryModel.id == skill_id
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=404,
            detail=f"Skill {skill_id} not found"
        )
    
    # Get category if exists
    skill_dict = skill.to_dict()
    
    if skill.category_id:
        category = db.query(SkillCategory).filter(
            SkillCategory.id == skill.category_id
        ).first()
        
        if category:
            skill_dict['category_name'] = category.category_name
            skill_dict['category_display_name'] = category.display_name
            skill_dict['category_icon'] = category.icon
    
    return skill_dict


@router.post("/", response_model=SkillsDictionary)
async def create_skill(
    skill: SkillsDictionaryCreate,
    db: Session = Depends(get_db)
):
    """
    Create new skill in dictionary
    
    Directly adds skill without validation queue
    """
    
    try:
        # Check if exists
        existing = db.query(SkillsDictionaryModel).filter(
            SkillsDictionaryModel.skill_name == skill.skill_name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Skill '{skill.skill_name}' already exists"
            )
        
        # Create
        db_skill = SkillsDictionaryModel(
            **skill.dict()
        )
        
        db.add(db_skill)
        db.commit()
        db.refresh(db_skill)
        
        return db_skill.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create skill: {str(e)}"
        )


@router.put("/{skill_id}", response_model=SkillsDictionary)
async def update_skill(
    skill_id: int,
    skill_update: SkillsDictionaryUpdate,
    validator_user: str = Query("system", description="User making update"),
    db: Session = Depends(get_db)
):
    """
    Update skill in dictionary
    
    Tracks changes in history if category is updated
    """
    
    try:
        skill = db.query(SkillsDictionaryModel).filter(
            SkillsDictionaryModel.id == skill_id
        ).first()
        
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill {skill_id} not found"
            )
        
        # Track category change
        old_category = skill.category_id
        
        # Update fields
        update_data = skill_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)
        
        skill.updated_at = datetime.now()
        
        # If category changed, log to history
        if 'category_id' in update_data and update_data['category_id'] != old_category:
            validator = SkillValidatorService(db)
            validator.update_skill_category(
                skill_id=skill_id,
                new_category_id=update_data['category_id'],
                validator_user=validator_user
            )
        else:
            db.commit()
        
        db.refresh(skill)
        
        return skill.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update skill: {str(e)}"
        )


@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: int,
    validator_user: str = Query("system"),
    db: Session = Depends(get_db)
):
    """
    Delete skill from dictionary (soft delete)
    
    Sets is_active = False instead of actual deletion
    """
    
    try:
        skill = db.query(SkillsDictionaryModel).filter(
            SkillsDictionaryModel.id == skill_id
        ).first()
        
        if not skill:
            raise HTTPException(
                status_code=404,
                detail=f"Skill {skill_id} not found"
            )
        
        # Soft delete
        skill.is_active = False
        skill.updated_at = datetime.now()
        
        # Log to history
        from app.models.validation_history import ValidationHistory
        from datetime import datetime
        
        history = ValidationHistory(
            skill_id=skill_id,
            validator_user=validator_user,
            action='deleted',
            notes='Soft delete'
        )
        db.add(history)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Skill '{skill.skill_name}' deleted",
            "skill_id": skill_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete skill: {str(e)}"
        )


@router.get("/search/name")
async def search_skills(
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search skills by name (autocomplete)
    
    Returns matching skills for autocomplete/search
    """
    
    try:
        skills = db.query(SkillsDictionaryModel).filter(
            or_(
                SkillsDictionaryModel.skill_name.ilike(f"%{query}%"),
                SkillsDictionaryModel.normalized_name.ilike(f"%{query}%")
            ),
            SkillsDictionaryModel.is_active == True
        ).limit(limit).all()
        
        return {
            "success": True,
            "count": len(skills),
            "skills": [
                {
                    'id': s.id,
                    'skill_name': s.skill_name,
                    'category_id': s.category_id,
                    'usage_count': s.usage_count
                }
                for s in skills
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )