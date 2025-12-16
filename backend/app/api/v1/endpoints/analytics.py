# Location: backend/app/api/v1/endpoints/analytics.py
"""
Analytics API Endpoints
Provides RESTful endpoints for job market analytics

Endpoints:
- GET /api/v1/analytics/health - Health check
- GET /api/v1/analytics/skills/demand - Get skills demand analysis
- GET /api/v1/analytics/skills/top - Get top N demanded skills
- GET /api/v1/analytics/skills/category/{category} - Get skills by category
- GET /api/v1/analytics/skills/categories - Get all categories
- GET /api/v1/analytics/skills/cooccurrence - Get skill co-occurrence
- GET /api/v1/analytics/skills/trends - Get skill demand trends
- GET /api/v1/analytics/skills/summary - Get quick summary

Author: Arya
Date: 2025-12-16
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.analytics.skill_demand import (
    SkillDemandService,
    get_skills_demand_report,
    get_top_skills_by_category
)

router = APIRouter()


@router.get("/health")
async def analytics_health_check():
    """
    Check if analytics service is running
    
    Returns:
        Simple health status
    
    Example:
        GET /api/v1/analytics/health
    """
    return {
        "status": "healthy",
        "service": "analytics",
        "version": "1.0.0",
        "module": "Skills Demand Analysis"
    }


@router.get("/skills/summary")
async def get_skills_summary(
    db: Session = Depends(get_db)
):
    """
    Get quick summary of skills analysis
    
    Returns:
    - Total jobs analyzed
    - Total unique skills
    - Average skills per job
    - Top 3 most demanded skills
    - Number of categories
    
    Example:
        GET /api/v1/analytics/skills/summary
    """
    try:
        service = SkillDemandService(db)
        jobs_data = service.extract_skills_from_jobs()
        
        if not jobs_data:
            return {
                "success": False,
                "error": "No tokenized jobs found in database",
                "hint": "Make sure jobs have been tokenized with skill data"
            }
        
        service.analyze_frequency(jobs_data)
        summary = service.generate_summary()
        
        return {
            "success": True,
            "data": summary
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/skills/demand")
async def get_skills_demand(
    limit: Optional[int] = Query(None, description="Maximum jobs to analyze"),
    top_n: int = Query(50, description="Number of top skills to return", ge=1, le=200),
    min_cooccurrence: int = Query(5, description="Minimum co-occurrence count", ge=2),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    location: Optional[str] = Query(None, description="Filter by location"),
    level: Optional[str] = Query(None, description="Filter by job level"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive skills demand analysis
    
    Returns:
    - Summary statistics
    - Frequency analysis
    - Co-occurrence patterns
    - Category distribution
    - Trend analysis (if date filters applied)
    
    Example:
        GET /api/v1/analytics/skills/demand?limit=1000&top_n=30
    """
    try:
        # Parse dates if provided
        filters = {}
        if date_from:
            try:
                filters['date_from'] = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date_from format. Use YYYY-MM-DD"
                )
        
        if date_to:
            try:
                filters['date_to'] = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date_to format. Use YYYY-MM-DD"
                )
        
        if location:
            filters['location'] = location
        if level:
            filters['level'] = level
        
        # Run analysis
        service = SkillDemandService(db)
        results = service.run_complete_analysis(
            limit=limit,
            top_n=top_n,
            min_cooccurrence=min_cooccurrence,
            **filters
        )
        
        if 'error' in results:
            return {
                "success": False,
                "error": results['error'],
                "hint": "Check that jobs have been tokenized with skill data"
            }
        
        return {
            "success": True,
            "data": results,
            "message": f"Analyzed {results['summary']['total_jobs_analyzed']} jobs successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/skills/top")
async def get_top_skills(
    n: int = Query(50, description="Number of top skills", ge=1, le=200),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get top N most demanded skills
    
    Parameters:
    - n: Number of skills to return (1-200)
    - category: Optional category filter
    
    Returns:
    - List of top skills with demand counts and percentages
    
    Example:
        GET /api/v1/analytics/skills/top?n=30&category=programming_language
    """
    try:
        if category:
            skills = get_top_skills_by_category(db, category=category, n=n)
        else:
            service = SkillDemandService(db)
            jobs_data = service.extract_skills_from_jobs()
            
            if not jobs_data:
                return {
                    "success": False,
                    "error": "No tokenized jobs found",
                    "data": {"count": 0, "skills": []}
                }
            
            service.analyze_frequency(jobs_data)
            skills = service.get_top_skills(n=n)
        
        return {
            "success": True,
            "data": {
                "count": len(skills),
                "category": category,
                "skills": skills
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get top skills: {str(e)}"
        )


@router.get("/skills/categories")
async def get_skill_categories(
    db: Session = Depends(get_db)
):
    """
    Get skill distribution across categories
    
    Returns:
    - List of categories with statistics
    - Unique skill counts per category
    - Total demand per category
    
    Example:
        GET /api/v1/analytics/skills/categories
    """
    try:
        service = SkillDemandService(db)
        jobs_data = service.extract_skills_from_jobs()
        
        if not jobs_data:
            return {
                "success": False,
                "error": "No tokenized jobs found",
                "data": {"total_categories": 0, "categories": []}
            }
        
        service.analyze_frequency(jobs_data)
        category_dist = service.get_category_distribution()
        
        return {
            "success": True,
            "data": category_dist
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get categories: {str(e)}"
        )


@router.get("/skills/category/{category}")
async def get_skills_by_category(
    category: str,
    n: int = Query(20, description="Number of skills to return", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top skills for a specific category
    
    Parameters:
    - category: Skill category (e.g., 'programming_language', 'frontend', 'backend')
    - n: Number of skills to return
    
    Returns:
    - List of top skills in the specified category
    
    Example:
        GET /api/v1/analytics/skills/category/programming_language?n=20
    """
    try:
        skills = get_top_skills_by_category(db, category=category, n=n)
        
        if not skills:
            raise HTTPException(
                status_code=404,
                detail=f"Category '{category}' not found or has no skills"
            )
        
        return {
            "success": True,
            "data": {
                "category": category,
                "count": len(skills),
                "skills": skills
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get category skills: {str(e)}"
        )


@router.get("/skills/cooccurrence")
async def get_skill_cooccurrence(
    min_support: int = Query(5, description="Minimum co-occurrence count", ge=2),
    limit: int = Query(100, description="Maximum pairs to return", ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get skill co-occurrence analysis
    
    Shows which skills frequently appear together in job postings
    
    Parameters:
    - min_support: Minimum number of times skills must appear together
    - limit: Maximum number of pairs to return
    
    Returns:
    - List of skill pairs with co-occurrence metrics
    - Lift scores (measure of association strength)
    - Confidence scores
    
    Example:
        GET /api/v1/analytics/skills/cooccurrence?min_support=10&limit=50
    """
    try:
        service = SkillDemandService(db)
        jobs_data = service.extract_skills_from_jobs()
        
        if not jobs_data:
            return {
                "success": False,
                "error": "No tokenized jobs found",
                "data": {"total_pairs": 0, "pairs": []}
            }
        
        service.analyze_frequency(jobs_data)
        cooccurrence_results = service.analyze_cooccurrence(
            jobs_data,
            min_support=min_support
        )
        
        # Limit results
        pairs = cooccurrence_results['pairs'][:limit]
        
        return {
            "success": True,
            "data": {
                "total_pairs": len(pairs),
                "min_support": min_support,
                "pairs": pairs
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Co-occurrence analysis failed: {str(e)}"
        )


@router.get("/skills/trends")
async def get_skill_trends(
    period: str = Query("month", description="Time period (day/week/month)"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get skill demand trends over time
    
    Parameters:
    - period: Aggregation period ('day', 'week', or 'month')
    - date_from: Start date for analysis
    - date_to: End date for analysis
    
    Returns:
    - Time series data of skill demand
    - Top skills per period
    - Job counts per period
    
    Example:
        GET /api/v1/analytics/skills/trends?period=month&date_from=2024-01-01
    """
    try:
        # Validate period
        if period not in ['day', 'week', 'month']:
            raise HTTPException(
                status_code=400,
                detail="Period must be 'day', 'week', or 'month'"
            )
        
        # Parse dates
        filters = {}
        if date_from:
            try:
                filters['date_from'] = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date_from format. Use YYYY-MM-DD"
                )
        
        if date_to:
            try:
                filters['date_to'] = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date_to format. Use YYYY-MM-DD"
                )
        
        # Get data
        service = SkillDemandService(db)
        jobs_data = service.extract_skills_from_jobs(**filters)
        
        if not jobs_data:
            raise HTTPException(
                status_code=404,
                detail="No jobs found in specified date range"
            )
        
        # Analyze trends
        trends = service.analyze_trends(jobs_data, period=period)
        
        return {
            "success": True,
            "data": trends
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trend analysis failed: {str(e)}"
        )