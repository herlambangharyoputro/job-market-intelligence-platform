# Location: backend/app/schemas/validation_queue.py
"""
Validation Queue Schemas
Module #5: Skill Validation System 
Date: 2025-12-16
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class QueueStatus(str, Enum):
    """Queue status enum"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class ValidationAction(str, Enum):
    """Validation action enum"""
    approve = "approve"
    reject = "reject"
    skip = "skip"


class ValidationQueueBase(BaseModel):
    """Base schema for validation queue"""
    skill_name: str = Field(..., max_length=100)
    source_count: int = 1
    priority: int = 0


class ValidationQueueCreate(ValidationQueueBase):
    """Schema for creating queue item"""
    suggested_category_id: Optional[int] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    context_sample: Optional[list[dict[str, Any]]] = None
    metadata: Optional[dict[str, Any]] = None


class ValidationQueueUpdate(BaseModel):
    """Schema for updating queue item"""
    status: Optional[QueueStatus] = None
    assigned_to: Optional[str] = None
    suggested_category_id: Optional[int] = None
    priority: Optional[int] = None


class ValidationQueue(ValidationQueueBase):
    """Schema for validation queue response"""
    id: int
    status: str
    assigned_to: Optional[str] = None
    suggested_category_id: Optional[int] = None
    confidence_score: Optional[float] = None
    context_sample: Optional[list[dict[str, Any]]] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ValidationQueueWithCategory(ValidationQueue):
    """Schema with suggested category details"""
    suggested_category_name: Optional[str] = None
    suggested_category_display: Optional[str] = None


class ValidationQueueList(BaseModel):
    """Schema for list of queue items"""
    total: int
    pending: int
    in_progress: int
    completed: int
    skipped: int
    items: list[ValidationQueue]


class ValidateSkillRequest(BaseModel):
    """Schema for skill validation request"""
    action: ValidationAction
    category_id: Optional[int] = None
    notes: Optional[str] = None
    validator_user: Optional[str] = "system"


class ValidateSkillResponse(BaseModel):
    """Schema for validation response"""
    success: bool
    message: str
    skill_id: Optional[int] = None
    queue_item_id: int
    action: str


class BulkValidateRequest(BaseModel):
    """Schema for bulk validation"""
    queue_ids: list[int] = Field(..., min_items=1, max_items=100)
    action: ValidationAction
    category_id: Optional[int] = None
    validator_user: Optional[str] = "system"


class BulkValidateResponse(BaseModel):
    """Schema for bulk validation response"""
    success: bool
    total: int
    succeeded: int
    failed: int
    results: list[ValidateSkillResponse]