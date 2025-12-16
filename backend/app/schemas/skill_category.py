# Location: backend/app/schemas/skill_category.py
"""
Skill Category Schemas
Module #5: Skill Validation System

Pydantic schemas for request/response validation 
Date: 2025-12-16
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SkillCategoryBase(BaseModel):
    """Base schema for skill category"""
    category_name: str = Field(..., max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    parent_category_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True


class SkillCategoryCreate(SkillCategoryBase):
    """Schema for creating skill category"""
    pass


class SkillCategoryUpdate(BaseModel):
    """Schema for updating skill category"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class SkillCategory(SkillCategoryBase):
    """Schema for skill category response"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SkillCategoryList(BaseModel):
    """Schema for list of categories"""
    total: int
    categories: list[SkillCategory]