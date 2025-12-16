# Location: backend/app/schemas/validation_history.py
"""
Validation History Schemas
Module #5: Skill Validation System

Author: Arya
Date: 2025-12-16
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class HistoryAction(str, Enum):
    """History action enum"""
    created = "created"
    approved = "approved"
    rejected = "rejected"
    updated = "updated"
    merged = "merged"
    deleted = "deleted"


class ValidationHistoryBase(BaseModel):
    """Base schema for validation history"""
    skill_id: int
    validator_user: Optional[str] = None
    action: HistoryAction
    notes: Optional[str] = None


class ValidationHistoryCreate(ValidationHistoryBase):
    """Schema for creating history entry"""
    old_category_id: Optional[int] = None
    new_category_id: Optional[int] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class ValidationHistory(ValidationHistoryBase):
    """Schema for validation history response"""
    id: int
    old_category_id: Optional[int] = None
    new_category_id: Optional[int] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ValidationHistoryWithDetails(ValidationHistory):
    """Schema with skill and category details"""
    skill_name: Optional[str] = None
    old_category_name: Optional[str] = None
    new_category_name: Optional[str] = None


class ValidationHistoryList(BaseModel):
    """Schema for list of history entries"""
    total: int
    entries: list[ValidationHistory]


class ValidationStatsResponse(BaseModel):
    """Schema for validation statistics"""
    total_skills: int
    validated: int
    pending: int
    rejected: int
    validation_rate: float
    total_queue_items: int
    queue_pending: int
    queue_completed: int
    total_categories: int
    active_categories: int
    recent_activity: list[ValidationHistory]