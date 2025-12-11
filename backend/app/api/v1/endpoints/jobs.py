from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.job import Job, JobCreate
from app.models.job import Job as JobModel

router = APIRouter()

@router.get("/", response_model=List[Job])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all jobs"""
    jobs = db.query(JobModel).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=Job)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job by ID"""
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/", response_model=Job)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create new job"""
    db_job = JobModel(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job