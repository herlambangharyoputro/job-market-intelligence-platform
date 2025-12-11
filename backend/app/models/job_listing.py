from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

class JobListingBase(BaseModel):
    """Base schema untuk JobListing"""
    judul: str = Field(..., description="Judul/posisi pekerjaan")
    perusahaan: str = Field(..., description="Nama perusahaan")
    lokasi: Optional[str] = Field(None, description="Lokasi singkat")
    lokasi_detail: Optional[str] = Field(None, description="Lokasi lengkap")
    tipe_pekerjaan: Optional[str] = Field(None, description="Tipe pekerjaan")
    level: Optional[str] = Field(None, description="Level posisi")
    fungsi: Optional[str] = Field(None, description="Fungsi pekerjaan")
    pendidikan: Optional[str] = Field(None, description="Minimal pendidikan")
    gaji: Optional[str] = Field(None, description="Range gaji")
    industri: Optional[str] = Field(None, description="Industri perusahaan")
    jumlah_karyawan: Optional[str] = Field(None, description="Jumlah karyawan")
    tanggal_posting: Optional[datetime] = Field(None, description="Tanggal posting")
    posting_relatif: Optional[str] = Field(None, description="Waktu posting relatif")
    waktu_scraping: datetime = Field(..., description="Waktu scraping")
    deskripsi_singkat: Optional[str] = Field(None, description="Deskripsi singkat")
    tanggung_jawab: Optional[str] = Field(None, description="Tanggung jawab")
    kualifikasi: Optional[str] = Field(None, description="Kualifikasi")
    keahlian: Optional[str] = Field(None, description="Keahlian")
    benefit: Optional[str] = Field(None, description="Benefit")
    url: str = Field(..., description="URL lowongan")

class JobListingCreate(JobListingBase):
    """Schema untuk membuat job listing baru"""
    pass

class JobListingUpdate(BaseModel):
    """Schema untuk update job listing (semua field optional)"""
    judul: Optional[str] = None
    perusahaan: Optional[str] = None
    lokasi: Optional[str] = None
    lokasi_detail: Optional[str] = None
    tipe_pekerjaan: Optional[str] = None
    level: Optional[str] = None
    fungsi: Optional[str] = None
    pendidikan: Optional[str] = None
    gaji: Optional[str] = None
    industri: Optional[str] = None
    jumlah_karyawan: Optional[str] = None
    tanggal_posting: Optional[datetime] = None
    posting_relatif: Optional[str] = None
    waktu_scraping: Optional[datetime] = None
    deskripsi_singkat: Optional[str] = None
    tanggung_jawab: Optional[str] = None
    kualifikasi: Optional[str] = None
    keahlian: Optional[str] = None
    benefit: Optional[str] = None
    url: Optional[str] = None

class JobListing(JobListingBase):
    """Schema untuk response job listing (dengan ID dan timestamps)"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JobListingList(BaseModel):
    """Schema untuk response list job listings dengan pagination"""
    total: int
    page: int
    page_size: int
    data: list[JobListing]

class JobListingFilter(BaseModel):
    """Schema untuk filtering job listings"""
    judul: Optional[str] = Field(None, description="Filter berdasarkan judul")
    perusahaan: Optional[str] = Field(None, description="Filter berdasarkan perusahaan")
    lokasi: Optional[str] = Field(None, description="Filter berdasarkan lokasi")
    tipe_pekerjaan: Optional[str] = Field(None, description="Filter berdasarkan tipe pekerjaan")
    level: Optional[str] = Field(None, description="Filter berdasarkan level")
    industri: Optional[str] = Field(None, description="Filter berdasarkan industri")
    min_gaji: Optional[float] = Field(None, description="Gaji minimum")
    max_gaji: Optional[float] = Field(None, description="Gaji maximum")

class JobListingStats(BaseModel):
    """Schema untuk statistik job listings"""
    total_jobs: int
    total_companies: int
    total_locations: int
    job_types: dict[str, int]
    job_levels: dict[str, int]
    industries: dict[str, int]