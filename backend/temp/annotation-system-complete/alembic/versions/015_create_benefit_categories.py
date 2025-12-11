"""create benefit_categories table

Revision ID: 015
Revises: 014
Create Date: 2025-12-11 11:10:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '015'
down_revision: Union[str, None] = '014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create benefit_categories table"""
    op.create_table(
        'benefit_categories',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Benefit identification
        sa.Column('benefit_code', sa.String(100), nullable=False, unique=True, comment='Unique benefit code'),
        sa.Column('benefit_name', sa.String(255), nullable=False, index=True, comment='Benefit name'),
        sa.Column('benefit_name_en', sa.String(255), nullable=True, comment='English name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Benefit description'),
        
        # Hierarchy and categorization
        sa.Column('parent_benefit_id', sa.Integer(), nullable=True, index=True, comment='Parent benefit category'),
        sa.Column('level', sa.Integer(), default=0, comment='Hierarchy level'),
        sa.Column('category_type', sa.Enum('compensation', 'health', 'work_life', 'development', 'perks', 'insurance', 'retirement', 'other', name='benefit_category_type'), nullable=False, index=True),
        
        # Benefit details
        sa.Column('is_monetary', sa.Boolean(), default=False, comment='Is this a monetary benefit'),
        sa.Column('typical_value', sa.String(100), nullable=True, comment='Typical value or range'),
        sa.Column('value_type', sa.Enum('fixed', 'percentage', 'variable', 'unlimited', name='benefit_value_type'), nullable=True),
        
        # Recognition patterns
        sa.Column('keywords', sa.JSON(), nullable=True, comment='Keywords to identify this benefit'),
        sa.Column('patterns', sa.JSON(), nullable=True, comment='Regex patterns for extraction'),
        sa.Column('synonyms', sa.JSON(), nullable=True, comment='Alternative names'),
        sa.Column('examples', sa.JSON(), nullable=True, comment='Example phrases'),
        
        # Market data
        sa.Column('prevalence_rate', sa.Numeric(5, 2), nullable=True, comment='How common is this benefit (%)'),
        sa.Column('job_count', sa.Integer(), default=0, comment='Number of jobs offering this benefit'),
        sa.Column('company_count', sa.Integer(), default=0, comment='Number of companies offering'),
        sa.Column('popularity_score', sa.Integer(), default=0, comment='Popularity score (0-100)'),
        
        # Industry insights
        sa.Column('common_in_industries', sa.JSON(), nullable=True, comment='Industries where this is common'),
        sa.Column('common_for_levels', sa.JSON(), nullable=True, comment='Job levels that typically get this'),
        sa.Column('typical_company_sizes', sa.JSON(), nullable=True, comment='Company sizes offering this'),
        
        # Attractiveness
        sa.Column('attractiveness_score', sa.Integer(), default=50, comment='How attractive this benefit is (0-100)'),
        sa.Column('impact_on_salary', sa.Numeric(5, 2), nullable=True, comment='Estimated impact on total compensation (%)'),
        sa.Column('retention_impact', sa.Enum('low', 'medium', 'high', 'critical', name='impact_level'), nullable=True, comment='Impact on employee retention'),
        
        # Display settings
        sa.Column('icon', sa.String(50), nullable=True, comment='Icon identifier'),
        sa.Column('color_code', sa.String(7), nullable=True, comment='Color for UI'),
        sa.Column('display_order', sa.Integer(), default=0),
        
        # Verification and quality
        sa.Column('is_standard', sa.Boolean(), default=False, comment='Standard benefit (legally required)'),
        sa.Column('requires_verification', sa.Boolean(), default=False, comment='Needs manual verification'),
        sa.Column('confidence_threshold', sa.Numeric(5, 4), default=0.7, comment='Minimum confidence for auto-tagging'),
        
        # Status
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('is_featured', sa.Boolean(), default=False, comment='Featured in UI'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        sa.ForeignKeyConstraint(['parent_benefit_id'], ['benefit_categories.id'], ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_benefit_categories_hierarchy', 'benefit_categories', ['parent_benefit_id', 'level'])
    op.create_index('idx_benefit_categories_type', 'benefit_categories', ['category_type', 'is_active'])
    op.create_index('idx_benefit_categories_popularity', 'benefit_categories', ['popularity_score', 'prevalence_rate'])
    op.create_index('idx_benefit_categories_stats', 'benefit_categories', ['job_count', 'company_count'])
    op.create_index('idx_benefit_categories_attractiveness', 'benefit_categories', ['attractiveness_score', 'retention_impact'])


def downgrade() -> None:
    """Drop benefit_categories table"""
    op.drop_index('idx_benefit_categories_attractiveness', 'benefit_categories')
    op.drop_index('idx_benefit_categories_stats', 'benefit_categories')
    op.drop_index('idx_benefit_categories_popularity', 'benefit_categories')
    op.drop_index('idx_benefit_categories_type', 'benefit_categories')
    op.drop_index('idx_benefit_categories_hierarchy', 'benefit_categories')
    op.drop_table('benefit_categories')
    op.execute('DROP TYPE IF EXISTS benefit_category_type')
    op.execute('DROP TYPE IF EXISTS benefit_value_type')
    op.execute('DROP TYPE IF EXISTS impact_level')
