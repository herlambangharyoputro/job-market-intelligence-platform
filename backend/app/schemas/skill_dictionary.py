# Location: backend/app/schemas/skill_dictionary.py
"""
Skills Dictionary Schemas
Module #5: Skill Validation System 
Date: 2025-12-16
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class ValidationStatus(str, Enum):
    """Validation status enum"""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SkillsDictionaryBase(BaseModel):
    """Base schema for skills dictionary"""
    skill_name: str = Field(..., max_length=100)
    normalized_name: str = Field(..., max_length=100)
    category_id: Optional[int] = None
    subcategory: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class SkillsDictionaryCreate(SkillsDictionaryBase):
    """Schema for creating skill in dictionary"""
    is_validated: bool = False
    validation_status: ValidationStatus = ValidationStatus.pending
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[dict[str, Any]] = None


class SkillsDictionaryUpdate(BaseModel):
    """Schema for updating skill in dictionary"""
    normalized_name: Optional[str] = None
    category_id: Optional[int] = None
    subcategory: Optional[str] = None
    is_validated: Optional[bool] = None
    is_active: Optional[bool] = None
    validation_status: Optional[ValidationStatus] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    description: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class SkillsDictionary(SkillsDictionaryBase):
    """Schema for skills dictionary response"""
    id: int
    is_validated: bool
    is_active: bool
    validation_status: str
    confidence_score: Optional[float] = None
    usage_count: int
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SkillsDictionaryWithCategory(SkillsDictionary):
    """Schema with category details"""
    category_name: Optional[str] = None
    category_display_name: Optional[str] = None
    category_icon: Optional[str] = None


class SkillsDictionaryList(BaseModel):
    """Schema for list of skills"""
    total: int
    validated: int
    pending: int
    rejected: int
    skills: list[SkillsDictionary]