"""create salary_ranges table

Revision ID: 013
Revises: 012
Create Date: 2025-12-11 11:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create salary_ranges table"""
    op.create_table(
        'salary_ranges',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Position details
        sa.Column('job_title', sa.String(500), nullable=False, index=True, comment='Job title/position'),
        sa.Column('job_title_normalized', sa.String(255), nullable=True, index=True, comment='Normalized job title'),
        sa.Column('job_level', sa.String(100), nullable=True, index=True, comment='Job level (Entry, Mid, Senior, etc)'),
        sa.Column('job_function', sa.String(255), nullable=True, index=True, comment='Job function/department'),
        
        # Location
        sa.Column('location', sa.String(255), nullable=True, index=True, comment='Location'),
        sa.Column('city', sa.String(100), nullable=True, index=True, comment='City'),
        sa.Column('province', sa.String(100), nullable=True, comment='Province'),
        
        # Industry
        sa.Column('industry', sa.String(255), nullable=True, index=True, comment='Industry sector'),
        sa.Column('company_size', sa.String(100), nullable=True, comment='Company size category'),
        
        # Salary data (in IDR)
        sa.Column('min_salary', sa.Numeric(15, 2), nullable=True, comment='Minimum salary'),
        sa.Column('max_salary', sa.Numeric(15, 2), nullable=True, comment='Maximum salary'),
        sa.Column('avg_salary', sa.Numeric(15, 2), nullable=True, index=True, comment='Average salary'),
        sa.Column('median_salary', sa.Numeric(15, 2), nullable=True, comment='Median salary'),
        sa.Column('percentile_25', sa.Numeric(15, 2), nullable=True, comment='25th percentile'),
        sa.Column('percentile_75', sa.Numeric(15, 2), nullable=True, comment='75th percentile'),
        
        # Currency and period
        sa.Column('currency', sa.String(10), default='IDR', comment='Currency code'),
        sa.Column('salary_period', sa.Enum('hourly', 'daily', 'monthly', 'yearly', name='salary_period'), default='monthly', comment='Salary period'),
        
        # Statistics
        sa.Column('sample_size', sa.Integer(), default=0, comment='Number of data points'),
        sa.Column('standard_deviation', sa.Numeric(15, 2), nullable=True, comment='Standard deviation'),
        sa.Column('confidence_level', sa.Numeric(5, 4), nullable=True, comment='Statistical confidence level'),
        
        # Data source and validity
        sa.Column('data_source', sa.String(100), nullable=True, comment='Source of salary data'),
        sa.Column('collection_method', sa.String(100), nullable=True, comment='How data was collected'),
        sa.Column('valid_from', sa.Date(), nullable=True, comment='Valid from date'),
        sa.Column('valid_until', sa.Date(), nullable=True, index=True, comment='Valid until date'),
        
        # Trending
        sa.Column('trend_direction', sa.Enum('increasing', 'stable', 'decreasing', name='trend_direction'), nullable=True, comment='Salary trend'),
        sa.Column('growth_rate', sa.Numeric(5, 2), nullable=True, comment='YoY growth rate percentage'),
        
        # Additional insights
        sa.Column('required_experience_years', sa.String(50), nullable=True, comment='Required experience'),
        sa.Column('top_skills', sa.JSON(), nullable=True, comment='Top skills for this position'),
        sa.Column('benefits_included', sa.JSON(), nullable=True, comment='Common benefits'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes'),
        
        # Status
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('is_verified', sa.Boolean(), default=False, comment='Verified by admin'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_salary_ranges_title_level', 'salary_ranges', ['job_title_normalized', 'job_level'])
    op.create_index('idx_salary_ranges_location', 'salary_ranges', ['city', 'province'])
    op.create_index('idx_salary_ranges_industry_function', 'salary_ranges', ['industry', 'job_function'])
    op.create_index('idx_salary_ranges_salary', 'salary_ranges', ['min_salary', 'max_salary'])
    op.create_index('idx_salary_ranges_validity', 'salary_ranges', ['valid_from', 'valid_until'])


def downgrade() -> None:
    """Drop salary_ranges table"""
    op.drop_index('idx_salary_ranges_validity', 'salary_ranges')
    op.drop_index('idx_salary_ranges_salary', 'salary_ranges')
    op.drop_index('idx_salary_ranges_industry_function', 'salary_ranges')
    op.drop_index('idx_salary_ranges_location', 'salary_ranges')
    op.drop_index('idx_salary_ranges_title_level', 'salary_ranges')
    op.drop_table('salary_ranges')
    op.execute('DROP TYPE IF EXISTS salary_period')
    op.execute('DROP TYPE IF EXISTS trend_direction')
