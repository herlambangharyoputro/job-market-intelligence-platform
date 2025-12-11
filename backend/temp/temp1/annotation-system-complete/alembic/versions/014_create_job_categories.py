"""create job_categories table

Revision ID: 014
Revises: 013
Create Date: 2025-12-11 11:05:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '014'
down_revision: Union[str, None] = '013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create job_categories table"""
    op.create_table(
        'job_categories',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Category identification
        sa.Column('category_code', sa.String(100), nullable=False, unique=True, comment='Unique category code'),
        sa.Column('category_name', sa.String(255), nullable=False, index=True, comment='Category name'),
        sa.Column('category_name_en', sa.String(255), nullable=True, comment='English name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Category description'),
        
        # Hierarchy
        sa.Column('parent_category_id', sa.Integer(), nullable=True, index=True, comment='Parent category'),
        sa.Column('level', sa.Integer(), default=0, comment='Hierarchy level (0=root, 1=main, 2=sub, 3=detail)'),
        sa.Column('path', sa.String(500), nullable=True, comment='Materialized path'),
        
        # Classification
        sa.Column('category_type', sa.Enum('industry', 'function', 'skill_area', 'job_family', 'specialty', name='category_type'), nullable=False, index=True),
        
        # Synonyms and keywords
        sa.Column('keywords', sa.JSON(), nullable=True, comment='Related keywords for classification'),
        sa.Column('synonyms', sa.JSON(), nullable=True, comment='Alternative category names'),
        
        # Classification rules
        sa.Column('classification_rules', sa.JSON(), nullable=True, comment='Rules for auto-classification'),
        sa.Column('required_keywords', sa.JSON(), nullable=True, comment='Keywords that must be present'),
        sa.Column('excluded_keywords', sa.JSON(), nullable=True, comment='Keywords that exclude this category'),
        
        # Statistics
        sa.Column('job_count', sa.Integer(), default=0, comment='Number of jobs in this category'),
        sa.Column('avg_salary', sa.Numeric(15, 2), nullable=True, comment='Average salary in category'),
        sa.Column('growth_rate', sa.Numeric(5, 2), nullable=True, comment='Category growth rate'),
        sa.Column('demand_score', sa.Integer(), default=0, comment='Demand score (0-100)'),
        
        # Skills association
        sa.Column('common_skills', sa.JSON(), nullable=True, comment='Most common skills in this category'),
        sa.Column('required_education', sa.JSON(), nullable=True, comment='Common education requirements'),
        
        # Market insights
        sa.Column('market_trend', sa.Enum('growing', 'stable', 'declining', 'emerging', name='market_trend'), nullable=True, index=True),
        sa.Column('competition_level', sa.Enum('low', 'medium', 'high', 'very_high', name='competition_level'), nullable=True),
        sa.Column('remote_friendly', sa.Boolean(), default=False, comment='Typically offers remote work'),
        
        # Display settings
        sa.Column('icon', sa.String(50), nullable=True, comment='Icon identifier'),
        sa.Column('color_code', sa.String(7), nullable=True, comment='Color for UI'),
        sa.Column('display_order', sa.Integer(), default=0, comment='Display order'),
        
        # Status
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('is_featured', sa.Boolean(), default=False, comment='Featured category'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        sa.ForeignKeyConstraint(['parent_category_id'], ['job_categories.id'], ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_job_categories_hierarchy', 'job_categories', ['parent_category_id', 'level'])
    op.create_index('idx_job_categories_type', 'job_categories', ['category_type', 'is_active'])
    op.create_index('idx_job_categories_stats', 'job_categories', ['job_count', 'demand_score'])
    op.create_index('idx_job_categories_path', 'job_categories', ['path'])
    op.create_index('idx_job_categories_trend', 'job_categories', ['market_trend', 'growth_rate'])


def downgrade() -> None:
    """Drop job_categories table"""
    op.drop_index('idx_job_categories_trend', 'job_categories')
    op.drop_index('idx_job_categories_path', 'job_categories')
    op.drop_index('idx_job_categories_stats', 'job_categories')
    op.drop_index('idx_job_categories_type', 'job_categories')
    op.drop_index('idx_job_categories_hierarchy', 'job_categories')
    op.drop_table('job_categories')
    op.execute('DROP TYPE IF EXISTS category_type')
    op.execute('DROP TYPE IF EXISTS market_trend')
    op.execute('DROP TYPE IF EXISTS competition_level')
