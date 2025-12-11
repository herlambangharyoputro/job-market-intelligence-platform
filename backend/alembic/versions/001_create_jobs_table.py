"""create jobs table

Revision ID: 001
Revises: 
Create Date: 2025-12-11 10:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create jobs table with all fields from scraped data"""
    op.create_table(
        'jobs',
        # Primary key
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Job information
        sa.Column('judul', sa.String(500), nullable=False, index=True, comment='Job title'),
        sa.Column('perusahaan', sa.String(255), nullable=True, index=True, comment='Company name'),
        sa.Column('lokasi', sa.String(255), nullable=True, index=True, comment='Location'),
        sa.Column('lokasi_detail', sa.Text(), nullable=True, comment='Detailed location'),
        
        # Job details
        sa.Column('tipe_pekerjaan', sa.String(100), nullable=True, index=True, comment='Job type: Full-time, Part-time, etc'),
        sa.Column('level', sa.String(100), nullable=True, index=True, comment='Job level: Entry, Mid, Senior, etc'),
        sa.Column('fungsi', sa.String(255), nullable=True, index=True, comment='Job function/department'),
        sa.Column('pendidikan', sa.String(255), nullable=True, comment='Education requirement'),
        
        # Salary
        sa.Column('gaji', sa.String(255), nullable=True, comment='Salary information (text)'),
        sa.Column('gaji_min', sa.Numeric(15, 2), nullable=True, comment='Parsed minimum salary'),
        sa.Column('gaji_max', sa.Numeric(15, 2), nullable=True, comment='Parsed maximum salary'),
        sa.Column('gaji_currency', sa.String(10), nullable=True, default='IDR', comment='Currency code'),
        
        # Company details
        sa.Column('industri', sa.String(255), nullable=True, index=True, comment='Industry'),
        sa.Column('jumlah_karyawan', sa.String(100), nullable=True, comment='Number of employees'),
        
        # Posting information
        sa.Column('tanggal_posting', sa.Date(), nullable=True, index=True, comment='Posting date'),
        sa.Column('posting_relatif', sa.String(100), nullable=True, comment='Relative posting time (e.g., "2 days ago")'),
        sa.Column('waktu_scraping', sa.DateTime(), nullable=True, comment='Scraping timestamp'),
        
        # Job description fields
        sa.Column('deskripsi_singkat', sa.Text(), nullable=True, comment='Short description'),
        sa.Column('tanggung_jawab', sa.Text(), nullable=True, comment='Responsibilities'),
        sa.Column('kualifikasi', sa.Text(), nullable=True, comment='Qualifications'),
        sa.Column('keahlian', sa.Text(), nullable=True, comment='Required skills'),
        sa.Column('benefit', sa.Text(), nullable=True, comment='Benefits'),
        
        # Source information
        # sa.Column('url', sa.String(1000), nullable=True, unique=True, comment='Job posting URL'),
        sa.Column('url', sa.String(1000), nullable=True, comment='Job posting URL'),
        sa.Column('source', sa.String(100), nullable=True, default='lokerid', comment='Data source'),
        
        # Processing flags
        sa.Column('is_processed', sa.Boolean(), default=False, index=True, comment='Data processing status'),
        sa.Column('is_annotated', sa.Boolean(), default=False, index=True, comment='Annotation status'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # Indexes
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create additional indexes
    op.create_index('idx_jobs_company_location', 'jobs', ['perusahaan', 'lokasi'])
    op.create_index('idx_jobs_level_fungsi', 'jobs', ['level', 'fungsi'])
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'])
    op.create_index('idx_jobs_processing_status', 'jobs', ['is_processed', 'is_annotated'])


def downgrade() -> None:
    """Drop jobs table"""
    op.drop_index('idx_jobs_processing_status', 'jobs')
    op.drop_index('idx_jobs_created_at', 'jobs')
    op.drop_index('idx_jobs_level_fungsi', 'jobs')
    op.drop_index('idx_jobs_company_location', 'jobs')
    op.drop_table('jobs')
