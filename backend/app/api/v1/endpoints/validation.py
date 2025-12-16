# Location: backend/app/api/v1/endpoints/validation.py
"""
Validation API Endpoints
Module #5: Skill Validation System

RESTful API for skill validation workflow

Author: Herlambang Haryo Putro
Date: 2025-12-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.validation_queue import (
    ValidationQueue,
    ValidationQueueList,
    ValidateSkillRequest,
    ValidateSkillResponse,
    BulkValidateRequest,
    BulkValidateResponse,
    QueueStatus
)
from app.schemas.validation_history import ValidationStatsResponse
from app.services.validation.skill_validator import SkillValidatorService
from app.services.validation.queue_manager import QueueManagerService
from app.models.validation_queue import ValidationQueue as ValidationQueueModel

router = APIRouter()


@router.get("/queue", response_model=ValidationQueueList)
async def get_validation_queue(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by skill name"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_priority: Optional[int] = Query(None, ge=0, le=100, description="Minimum priority"),
    sort_by: str = Query("priority", description="Sort field (priority/count/created)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """
    Get validation queue with filtering and pagination
    
    Returns list of skills awaiting validation
    """
    
    try:
        manager = QueueManagerService(db)
        
        items, total = manager.get_queue_items(
            skip=skip,
            limit=limit,
            status=status,
            search=search,
            category_id=category_id,
            min_priority=min_priority,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get stats
        stats = manager.get_queue_stats()
        
        return ValidationQueueList(
            total=total,
            pending=stats['pending'],
            in_progress=stats['in_progress'],
            completed=stats['completed'],
            skipped=stats['skipped'],
            items=[item.to_dict() for item in items]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue: {str(e)}"
        )


@router.get("/queue/{queue_id}", response_model=ValidationQueue)
async def get_queue_item(
    queue_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single queue item by ID
    """
    
    manager = QueueManagerService(db)
    item = manager.get_queue_item(queue_id)
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Queue item {queue_id} not found"
        )
    
    return item.to_dict()


@router.get("/queue/next/item", response_model=ValidationQueue)
async def get_next_queue_item(
    assigned_to: Optional[str] = Query(None, description="User identifier"),
    db: Session = Depends(get_db)
):
    """
    Get next item to review (highest priority)
    
    Automatically marks as in_progress if assigned_to is provided
    """
    
    manager = QueueManagerService(db)
    item = manager.get_next_item(assigned_to=assigned_to)
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail="No pending items in queue"
        )
    
    return item.to_dict()


@router.post("/validate/{queue_id}", response_model=ValidateSkillResponse)
async def validate_skill(
    queue_id: int,
    request: ValidateSkillRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a skill (approve/reject/skip)
    
    Actions:
    - approve: Add to dictionary with category
    - reject: Mark as rejected
    - skip: Skip for later review
    """
    
    try:
        # Get queue item
        manager = QueueManagerService(db)
        queue_item = manager.get_queue_item(queue_id)
        
        if not queue_item:
            raise HTTPException(
                status_code=404,
                detail=f"Queue item {queue_id} not found"
            )
        
        # Validate
        validator = SkillValidatorService(db)
        
        if request.action == "approve":
            if not request.category_id:
                raise HTTPException(
                    status_code=400,
                    detail="category_id required for approval"
                )
            
            skill = validator.approve_skill(
                queue_item=queue_item,
                category_id=request.category_id,
                validator_user=request.validator_user,
                notes=request.notes
            )
            
            return ValidateSkillResponse(
                success=True,
                message=f"Skill '{skill.skill_name}' approved",
                skill_id=skill.id,
                queue_item_id=queue_id,
                action="approved"
            )
        
        elif request.action == "reject":
            result = validator.reject_skill(
                queue_item=queue_item,
                validator_user=request.validator_user,
                notes=request.notes
            )
            
            return ValidateSkillResponse(
                success=True,
                message=f"Skill '{result['skill_name']}' rejected",
                skill_id=result['skill_id'],
                queue_item_id=queue_id,
                action="rejected"
            )
        
        elif request.action == "skip":
            result = validator.skip_skill(
                queue_item=queue_item,
                validator_user=request.validator_user
            )
            
            return ValidateSkillResponse(
                success=True,
                message=f"Skill '{result['skill_name']}' skipped",
                skill_id=None,
                queue_item_id=queue_id,
                action="skipped"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {request.action}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/validate/bulk", response_model=BulkValidateResponse)
async def bulk_validate_skills(
    request: BulkValidateRequest,
    db: Session = Depends(get_db)
):
    """
    Validate multiple skills at once
    
    Useful for batch operations (e.g., approve all skills in category)
    """
    
    try:
        if request.action == "approve" and not request.category_id:
            raise HTTPException(
                status_code=400,
                detail="category_id required for bulk approval"
            )
        
        validator = SkillValidatorService(db)
        
        results = validator.bulk_validate(
            queue_ids=request.queue_ids,
            action=request.action.value,
            category_id=request.category_id,
            validator_user=request.validator_user
        )
        
        # Convert to response format
        response_results = []
        for detail in results['details']:
            response_results.append(
                ValidateSkillResponse(
                    success=detail['success'],
                    message=detail.get('error', 'Success'),
                    skill_id=detail.get('skill_id'),
                    queue_item_id=detail['queue_id'],
                    action=request.action.value if detail['success'] else 'failed'
                )
            )
        
        return BulkValidateResponse(
            success=results['failed'] == 0,
            total=results['total'],
            succeeded=results['succeeded'],
            failed=results['failed'],
            results=response_results
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bulk validation failed: {str(e)}"
        )


@router.get("/stats", response_model=ValidationStatsResponse)
async def get_validation_stats(
    db: Session = Depends(get_db)
):
    """
    Get validation statistics for dashboard
    
    Returns:
    - Total skills and validation status breakdown
    - Queue statistics
    - Category counts
    - Recent activity
    """
    
    try:
        validator = SkillValidatorService(db)
        stats = validator.get_validation_stats()
        
        return ValidationStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.post("/queue/reset-stuck")
async def reset_stuck_items(
    hours: int = Query(24, ge=1, le=168, description="Hours threshold"),
    db: Session = Depends(get_db)
):
    """
    Reset items stuck in 'in_progress' status
    
    Useful for cleaning up abandoned reviews
    """
    
    try:
        manager = QueueManagerService(db)
        count = manager.reset_stuck_items(hours=hours)
        
        return {
            "success": True,
            "message": f"Reset {count} stuck items",
            "count": count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset stuck items: {str(e)}"
        )


@router.post("/queue/reprioritize")
async def reprioritize_queue(
    db: Session = Depends(get_db)
):
    """
    Recalculate priorities based on source_count
    
    Useful after bulk imports or data changes
    """
    
    try:
        manager = QueueManagerService(db)
        count = manager.reprioritize_queue()
        
        return {
            "success": True,
            "message": f"Reprioritized {count} items",
            "count": count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reprioritize: {str(e)}"
        )


@router.get("/health")
async def validation_health_check():
    """
    Health check for validation service
    """
    
    return {
        "status": "healthy",
        "service": "validation",
        "version": "1.0.0",
        "module": "Skill Validation System"
    }