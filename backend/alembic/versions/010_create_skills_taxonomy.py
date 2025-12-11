"""create skills_taxonomy table

Revision ID: 010
Revises: 009
Create Date: 2025-12-11 10:45:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create skills_taxonomy table"""
    op.create_table(
        'skills_taxonomy',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('skill_code', sa.String(100), nullable=False, unique=True, comment='Unique skill code'),
        sa.Column('skill_name', sa.String(255), nullable=False, index=True, comment='Skill name'),
        sa.Column('skill_name_en', sa.String(255), nullable=True, comment='English name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Skill description'),
        
        # Hierarchy
        sa.Column('parent_skill_id', sa.Integer(), nullable=True, index=True, comment='Parent skill for hierarchy'),
        sa.Column('level', sa.Integer(), default=0, comment='Hierarchy level (0=root, 1=category, 2=subcategory, etc)'),
        sa.Column('path', sa.String(500), nullable=True, comment='Materialized path (e.g., /1/5/12)'),
        
        # Classification
        sa.Column('skill_type', sa.Enum('hard', 'soft', 'technical', 'language', 'certification', 'tool', name='skill_type'), nullable=False, index=True),
        sa.Column('category', sa.String(100), nullable=True, index=True, comment='Main category (e.g., Programming, Design, Management)'),
        sa.Column('subcategory', sa.String(100), nullable=True, comment='Subcategory'),
        
        # Synonyms and related
        sa.Column('synonyms', sa.JSON(), nullable=True, comment='List of synonyms'),
        sa.Column('aliases', sa.JSON(), nullable=True, comment='Alternative names'),
        sa.Column('related_skills', sa.JSON(), nullable=True, comment='List of related skill IDs'),
        
        # Market data
        sa.Column('demand_level', sa.Enum('low', 'medium', 'high', 'very_high', name='demand_level'), nullable=True, index=True),
        sa.Column('avg_salary_impact', sa.Numeric(10, 2), nullable=True, comment='Average salary impact percentage'),
        sa.Column('job_count', sa.Integer(), default=0, comment='Number of jobs requiring this skill'),
        sa.Column('trending_score', sa.Numeric(5, 2), nullable=True, comment='Trending score'),
        
        # Metadata
        sa.Column('difficulty_level', sa.Enum('beginner', 'intermediate', 'advanced', 'expert', name='difficulty_level'), nullable=True),
        sa.Column('learning_resources', sa.JSON(), nullable=True, comment='Links to learning resources'),
        sa.Column('industry_specific', sa.JSON(), nullable=True, comment='List of specific industries'),
        
        # Status
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('is_verified', sa.Boolean(), default=False, comment='Verified by admin'),
        sa.Column('usage_count', sa.Integer(), default=0, comment='How many times used in annotations'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # sa.ForeignKeyConstraint(['parent_skill_id'], ['skills_taxonomy.id'], ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_skills_taxonomy_hierarchy', 'skills_taxonomy', ['parent_skill_id', 'level'])
    op.create_index('idx_skills_taxonomy_type_category', 'skills_taxonomy', ['skill_type', 'category'])
    op.create_index('idx_skills_taxonomy_demand', 'skills_taxonomy', ['demand_level', 'job_count'])
    op.create_index('idx_skills_taxonomy_path', 'skills_taxonomy', ['path'])


def downgrade() -> None:
    """Drop skills_taxonomy table"""
    op.drop_index('idx_skills_taxonomy_path', 'skills_taxonomy')
    op.drop_index('idx_skills_taxonomy_demand', 'skills_taxonomy')
    op.drop_index('idx_skills_taxonomy_type_category', 'skills_taxonomy')
    op.drop_index('idx_skills_taxonomy_hierarchy', 'skills_taxonomy')
    op.drop_table('skills_taxonomy')
    op.execute('DROP TYPE IF EXISTS skill_type')
    op.execute('DROP TYPE IF EXISTS demand_level')
    op.execute('DROP TYPE IF EXISTS difficulty_level')
