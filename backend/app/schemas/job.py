from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    description: str
    company: str
    location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True