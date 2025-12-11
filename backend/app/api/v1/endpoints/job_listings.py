"""
API Endpoints untuk Job Listings
Menyediakan CRUD operations dan filtering untuk data lowongan kerja
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from app.database import get_db
from app.schemas.job_listing import (
    JobListing,
    JobListingCreate,
    JobListingUpdate,
    JobListingList,
    JobListingFilter,
    JobListingStats
)
from app.models.job_listing import JobListing as JobListingModel

router = APIRouter()

@router.get("/", response_model=JobListingList)
def get_job_listings(
    skip: int = Query(0, ge=0, description="Offset untuk pagination"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah data per halaman"),
    judul: Optional[str] = Query(None, description="Filter berdasarkan judul"),
    perusahaan: Optional[str] = Query(None, description="Filter berdasarkan perusahaan"),
    lokasi: Optional[str] = Query(None, description="Filter berdasarkan lokasi"),
    tipe_pekerjaan: Optional[str] = Query(None, description="Filter berdasarkan tipe pekerjaan"),
    level: Optional[str] = Query(None, description="Filter berdasarkan level"),
    industri: Optional[str] = Query(None, description="Filter berdasarkan industri"),
    search: Optional[str] = Query(None, description="Search di judul, perusahaan, atau deskripsi"),
    db: Session = Depends(get_db)
):
    """
    Get list of job listings dengan pagination dan filtering
    """
    # Build query
    query = db.query(JobListingModel)
    
    # Apply filters
    if judul:
        query = query.filter(JobListingModel.judul.ilike(f"%{judul}%"))
    if perusahaan:
        query = query.filter(JobListingModel.perusahaan.ilike(f"%{perusahaan}%"))
    if lokasi:
        query = query.filter(JobListingModel.lokasi.ilike(f"%{lokasi}%"))
    if tipe_pekerjaan:
        query = query.filter(JobListingModel.tipe_pekerjaan == tipe_pekerjaan)
    if level:
        query = query.filter(JobListingModel.level == level)
    if industri:
        query = query.filter(JobListingModel.industri.ilike(f"%{industri}%"))
    
    # Search across multiple fields
    if search:
        search_filter = or_(
            JobListingModel.judul.ilike(f"%{search}%"),
            JobListingModel.perusahaan.ilike(f"%{search}%"),
            JobListingModel.deskripsi_singkat.ilike(f"%{search}%"),
            JobListingModel.keahlian.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    jobs = query.offset(skip).limit(limit).all()
    
    return JobListingList(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        data=jobs
    )

@router.get("/stats", response_model=JobListingStats)
def get_job_stats(db: Session = Depends(get_db)):
    """
    Get statistik job listings
    """
    # Total jobs
    total_jobs = db.query(JobListingModel).count()
    
    # Total unique companies
    total_companies = db.query(func.count(func.distinct(JobListingModel.perusahaan))).scalar()
    
    # Total unique locations
    total_locations = db.query(func.count(func.distinct(JobListingModel.lokasi))).scalar()
    
    # Job types distribution
    job_types_raw = db.query(
        JobListingModel.tipe_pekerjaan,
        func.count(JobListingModel.id)
    ).group_by(JobListingModel.tipe_pekerjaan).all()
    job_types = {jt[0] if jt[0] else "Unknown": jt[1] for jt in job_types_raw}
    
    # Job levels distribution
    job_levels_raw = db.query(
        JobListingModel.level,
        func.count(JobListingModel.id)
    ).group_by(JobListingModel.level).all()
    job_levels = {jl[0] if jl[0] else "Unknown": jl[1] for jl in job_levels_raw}
    
    # Industries distribution (top 10)
    industries_raw = db.query(
        JobListingModel.industri,
        func.count(JobListingModel.id)
    ).group_by(JobListingModel.industri).order_by(
        func.count(JobListingModel.id).desc()
    ).limit(10).all()
    industries = {ind[0] if ind[0] else "Unknown": ind[1] for ind in industries_raw}
    
    return JobListingStats(
        total_jobs=total_jobs,
        total_companies=total_companies,
        total_locations=total_locations,
        job_types=job_types,
        job_levels=job_levels,
        industries=industries
    )

@router.get("/{job_id}", response_model=JobListing)
def get_job_listing(job_id: int, db: Session = Depends(get_db)):
    """
    Get job listing by ID
    """
    job = db.query(JobListingModel).filter(JobListingModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")
    return job

@router.post("/", response_model=JobListing)
def create_job_listing(job: JobListingCreate, db: Session = Depends(get_db)):
    """
    Create new job listing
    """
    # Check if URL already exists
    existing = db.query(JobListingModel).filter(JobListingModel.url == job.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Job listing with this URL already exists")
    
    db_job = JobListingModel(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.put("/{job_id}", response_model=JobListing)
def update_job_listing(
    job_id: int,
    job_update: JobListingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update job listing
    """
    db_job = db.query(JobListingModel).filter(JobListingModel.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job listing not found")
    
    # Update only provided fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job

@router.delete("/{job_id}")
def delete_job_listing(job_id: int, db: Session = Depends(get_db)):
    """
    Delete job listing
    """
    db_job = db.query(JobListingModel).filter(JobListingModel.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job listing not found")
    
    db.delete(db_job)
    db.commit()
    return {"message": "Job listing deleted successfully", "id": job_id}

@router.get("/companies/list", response_model=List[str])
def get_companies(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get list of unique companies
    """
    companies = db.query(JobListingModel.perusahaan).distinct().limit(limit).all()
    return [c[0] for c in companies if c[0]]

@router.get("/locations/list", response_model=List[str])
def get_locations(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get list of unique locations
    """
    locations = db.query(JobListingModel.lokasi).distinct().limit(limit).all()
    return [loc[0] for loc in locations if loc[0]]

@router.get("/industries/list", response_model=List[str])
def get_industries(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get list of unique industries
    """
    industries = db.query(JobListingModel.industri).distinct().limit(limit).all()
    return [ind[0] for ind in industries if ind[0]]