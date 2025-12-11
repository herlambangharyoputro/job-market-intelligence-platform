"""create company_profiles table

Revision ID: 012
Revises: 011
Create Date: 2025-12-11 10:55:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create company_profiles table"""
    op.create_table(
        'company_profiles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Company identification
        sa.Column('company_name', sa.String(255), nullable=False, unique=True, index=True, comment='Company name'),
        sa.Column('company_name_normalized', sa.String(255), nullable=True, index=True, comment='Normalized company name'),
        sa.Column('legal_name', sa.String(255), nullable=True, comment='Legal company name'),
        sa.Column('aliases', sa.JSON(), nullable=True, comment='Alternative company names'),
        
        # Company details
        sa.Column('industry', sa.String(255), nullable=True, index=True, comment='Industry sector'),
        sa.Column('sub_industry', sa.String(255), nullable=True, comment='Sub-industry'),
        sa.Column('company_type', sa.Enum('startup', 'sme', 'corporate', 'multinational', 'government', 'ngo', name='company_type'), nullable=True, index=True),
        sa.Column('size_category', sa.String(100), nullable=True, index=True, comment='Company size (e.g., 1-50, 51-200, etc)'),
        sa.Column('employee_count', sa.Integer(), nullable=True, comment='Approximate number of employees'),
        
        # Contact and location
        sa.Column('headquarters_location', sa.String(255), nullable=True, comment='HQ location'),
        sa.Column('website', sa.String(500), nullable=True, comment='Company website'),
        sa.Column('email', sa.String(255), nullable=True, comment='Contact email'),
        sa.Column('phone', sa.String(50), nullable=True, comment='Contact phone'),
        sa.Column('address', sa.Text(), nullable=True, comment='Full address'),
        
        # Social media
        sa.Column('linkedin_url', sa.String(500), nullable=True, comment='LinkedIn URL'),
        sa.Column('facebook_url', sa.String(500), nullable=True, comment='Facebook URL'),
        sa.Column('twitter_url', sa.String(500), nullable=True, comment='Twitter URL'),
        sa.Column('instagram_url', sa.String(500), nullable=True, comment='Instagram URL'),
        
        # Description
        sa.Column('description', sa.Text(), nullable=True, comment='Company description'),
        sa.Column('mission', sa.Text(), nullable=True, comment='Company mission'),
        sa.Column('vision', sa.Text(), nullable=True, comment='Company vision'),
        sa.Column('values', sa.JSON(), nullable=True, comment='Company values'),
        
        # Hiring statistics
        sa.Column('total_job_postings', sa.Integer(), default=0, comment='Total job postings'),
        sa.Column('active_job_postings', sa.Integer(), default=0, comment='Currently active postings'),
        sa.Column('avg_salary_offered', sa.Numeric(15, 2), nullable=True, comment='Average salary'),
        sa.Column('most_common_positions', sa.JSON(), nullable=True, comment='Most frequently posted positions'),
        sa.Column('hiring_frequency', sa.String(50), nullable=True, comment='How often they hire'),
        
        # Reputation metrics
        sa.Column('rating', sa.Numeric(3, 2), nullable=True, comment='Company rating (0-5)'),
        sa.Column('review_count', sa.Integer(), default=0, comment='Number of reviews'),
        sa.Column('glassdoor_rating', sa.Numeric(3, 2), nullable=True, comment='Glassdoor rating'),
        sa.Column('indeed_rating', sa.Numeric(3, 2), nullable=True, comment='Indeed rating'),
        
        # Benefits and culture
        sa.Column('benefits_offered', sa.JSON(), nullable=True, comment='List of benefits'),
        sa.Column('work_culture', sa.JSON(), nullable=True, comment='Work culture attributes'),
        sa.Column('remote_work_policy', sa.String(100), nullable=True, comment='Remote work policy'),
        
        # Dates
        sa.Column('founded_year', sa.Integer(), nullable=True, comment='Year company was founded'),
        sa.Column('first_seen_date', sa.Date(), nullable=True, comment='First job posting date'),
        sa.Column('last_posting_date', sa.Date(), nullable=True, comment='Most recent job posting'),
        
        # Verification
        sa.Column('is_verified', sa.Boolean(), default=False, index=True, comment='Verified company'),
        sa.Column('verification_source', sa.String(100), nullable=True, comment='Verification source'),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_company_profiles_industry_type', 'company_profiles', ['industry', 'company_type'])
    op.create_index('idx_company_profiles_size', 'company_profiles', ['size_category', 'employee_count'])
    op.create_index('idx_company_profiles_hiring', 'company_profiles', ['total_job_postings', 'active_job_postings'])
    op.create_index('idx_company_profiles_rating', 'company_profiles', ['rating', 'review_count'])


def downgrade() -> None:
    """Drop company_profiles table"""
    op.drop_index('idx_company_profiles_rating', 'company_profiles')
    op.drop_index('idx_company_profiles_hiring', 'company_profiles')
    op.drop_index('idx_company_profiles_size', 'company_profiles')
    op.drop_index('idx_company_profiles_industry_type', 'company_profiles')
    op.drop_table('company_profiles')
    op.execute('DROP TYPE IF EXISTS company_type')
