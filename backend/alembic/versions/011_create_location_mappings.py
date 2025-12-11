"""create location_mappings table

Revision ID: 011
Revises: 010
Create Date: 2025-12-11 10:50:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create location_mappings table"""
    op.create_table(
        'location_mappings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Raw location data
        sa.Column('raw_location', sa.String(500), nullable=False, index=True, comment='Original location text from job posting'),
        
        # Normalized location
        sa.Column('normalized_location', sa.String(255), nullable=False, index=True, comment='Normalized location name'),
        sa.Column('city', sa.String(100), nullable=True, index=True, comment='City name'),
        sa.Column('province', sa.String(100), nullable=True, index=True, comment='Province/State'),
        sa.Column('country', sa.String(100), nullable=True, index=True, default='Indonesia', comment='Country'),
        sa.Column('country_code', sa.String(3), nullable=True, comment='ISO country code'),
        
        # Geographic coordinates
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True, comment='Latitude'),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True, comment='Longitude'),
        
        # Location hierarchy
        sa.Column('parent_location_id', sa.Integer(), nullable=True, index=True, comment='Parent location'),
        sa.Column('location_type', sa.Enum('country', 'province', 'city', 'district', 'area', 'remote', name='location_type'), nullable=True, index=True),
        sa.Column('level', sa.Integer(), default=0, comment='Hierarchy level'),
        
        # Alternative names
        sa.Column('aliases', sa.JSON(), nullable=True, comment='Alternative location names'),
        sa.Column('local_name', sa.String(255), nullable=True, comment='Local language name'),
        
        # Statistics
        sa.Column('job_count', sa.Integer(), default=0, comment='Number of jobs in this location'),
        sa.Column('company_count', sa.Integer(), default=0, comment='Number of companies in this location'),
        sa.Column('avg_salary', sa.Numeric(15, 2), nullable=True, comment='Average salary in this location'),
        
        # Metadata
        sa.Column('timezone', sa.String(50), nullable=True, comment='Timezone'),
        sa.Column('population', sa.Integer(), nullable=True, comment='Population size'),
        sa.Column('is_remote', sa.Boolean(), default=False, index=True, comment='Is remote work location'),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('confidence_score', sa.Numeric(5, 4), nullable=True, comment='Normalization confidence'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # sa.ForeignKeyConstraint(['parent_location_id'], ['location_mappings.id'], ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_location_mappings_geo', 'location_mappings', ['city', 'province', 'country'])
    op.create_index('idx_location_mappings_coordinates', 'location_mappings', ['latitude', 'longitude'])
    op.create_index('idx_location_mappings_stats', 'location_mappings', ['job_count', 'avg_salary'])
    op.create_index('idx_location_mappings_hierarchy', 'location_mappings', ['parent_location_id', 'level'])


def downgrade() -> None:
    """Drop location_mappings table"""
    op.drop_index('idx_location_mappings_hierarchy', 'location_mappings')
    op.drop_index('idx_location_mappings_stats', 'location_mappings')
    op.drop_index('idx_location_mappings_coordinates', 'location_mappings')
    op.drop_index('idx_location_mappings_geo', 'location_mappings')
    op.drop_table('location_mappings')
    op.execute('DROP TYPE IF EXISTS location_type')
