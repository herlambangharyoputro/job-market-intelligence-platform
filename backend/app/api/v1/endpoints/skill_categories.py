# Location: backend/app/api/v1/endpoints/skill_categories.py
"""
Skill Categories API Endpoints
Module #5: Skill Validation System

CRUD operations for skill categories

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.skill_category import (
    SkillCategory,
    SkillCategoryCreate,
    SkillCategoryUpdate,
    SkillCategoryList
)
from app.models.skill_category import SkillCategory as SkillCategoryModel

router = APIRouter()


@router.get("/", response_model=SkillCategoryList)
async def get_categories(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all skill categories
    
    Returns list of categories sorted by sort_order
    """
    
    try:
        query = db.query(SkillCategoryModel)
        
        if is_active is not None:
            query = query.filter(SkillCategoryModel.is_active == is_active)
        
        categories = query.order_by(SkillCategoryModel.sort_order).all()
        
        return SkillCategoryList(
            total=len(categories),
            categories=[cat.to_dict() for cat in categories]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get categories: {str(e)}"
        )


@router.get("/{category_id}", response_model=SkillCategory)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single category by ID
    """
    
    category = db.query(SkillCategoryModel).filter(
        SkillCategoryModel.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category {category_id} not found"
        )
    
    return category.to_dict()


@router.get("/name/{category_name}", response_model=SkillCategory)
async def get_category_by_name(
    category_name: str,
    db: Session = Depends(get_db)
):
    """
    Get category by name
    """
    
    category = db.query(SkillCategoryModel).filter(
        SkillCategoryModel.category_name == category_name
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category_name}' not found"
        )
    
    return category.to_dict()


@router.post("/", response_model=SkillCategory)
async def create_category(
    category: SkillCategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create new skill category
    """
    
    try:
        # Check if exists
        existing = db.query(SkillCategoryModel).filter(
            SkillCategoryModel.category_name == category.category_name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Category '{category.category_name}' already exists"
            )
        
        # Create
        db_category = SkillCategoryModel(
            **category.dict()
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        return db_category.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create category: {str(e)}"
        )


@router.put("/{category_id}", response_model=SkillCategory)
async def update_category(
    category_id: int,
    category_update: SkillCategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update skill category
    """
    
    try:
        category = db.query(SkillCategoryModel).filter(
            SkillCategoryModel.id == category_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found"
            )
        
        # Update fields
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        from datetime import datetime
        category.updated_at = datetime.now()
        
        db.commit()
        db.refresh(category)
        
        return category.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update category: {str(e)}"
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete category (soft delete by setting is_active=False)
    """
    
    try:
        category = db.query(SkillCategoryModel).filter(
            SkillCategoryModel.id == category_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found"
            )
        
        # Soft delete
        category.is_active = False
        from datetime import datetime
        category.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Category '{category.category_name}' deleted",
            "category_id": category_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete category: {str(e)}"
        )


@router.get("/{category_id}/skills")
async def get_category_skills(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get all skills in a category
    """
    
    try:
        from app.models.skill_dictionary import SkillsDictionary
        
        # Verify category exists
        category = db.query(SkillCategoryModel).filter(
            SkillCategoryModel.id == category_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found"
            )
        
        # Get skills
        query = db.query(SkillsDictionary).filter(
            SkillsDictionary.category_id == category_id,
            SkillsDictionary.is_active == True
        )
        
        total = query.count()
        skills = query.order_by(
            SkillsDictionary.usage_count.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            "success": True,
            "category": category.to_dict(),
            "total": total,
            "skills": [skill.to_dict() for skill in skills]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get category skills: {str(e)}"
        )