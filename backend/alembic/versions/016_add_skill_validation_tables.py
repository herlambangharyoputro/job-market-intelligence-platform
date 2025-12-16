# Location: backend/alembic/versions/016_add_skill_validation_tables.py
"""add skill validation tables

Revision ID: 016
Revises: 015
Create Date: 2025-12-16 16:00:00.000000

Module #5: Skill Validation System
Creates 5 new tables for supervised skill curation:
- skills_dictionary: Master skill list
- skill_aliases: Variations/synonyms
- skill_categories: Category taxonomy
- skill_validation_history: Audit trail
- validation_queue: Skills to review

Note: No foreign key constraints for flexibility
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    """Create skill validation tables"""
    
    # ================================================================
    # 1. SKILL CATEGORIES
    # ================================================================
    op.create_table(
        'skill_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('parent_category_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    op.create_index('idx_category_name', 'skill_categories', ['category_name'])
    op.create_index('idx_parent_category', 'skill_categories', ['parent_category_id'])
    
    # ================================================================
    # 2. SKILLS DICTIONARY (Master List)
    # ================================================================
    op.create_table(
        'skills_dictionary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(100), nullable=False, unique=True),
        sa.Column('normalized_name', sa.String(100), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('subcategory', sa.String(50), nullable=True),
        sa.Column('is_validated', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('validation_status', sa.Enum('pending', 'approved', 'rejected', name='validation_status_enum'), default='pending'),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    op.create_index('idx_skill_name', 'skills_dictionary', ['skill_name'])
    op.create_index('idx_normalized_name', 'skills_dictionary', ['normalized_name'])
    op.create_index('idx_category', 'skills_dictionary', ['category_id'])
    op.create_index('idx_validation_status', 'skills_dictionary', ['validation_status'])
    op.create_index('idx_is_validated', 'skills_dictionary', ['is_validated'])
    
    # ================================================================
    # 3. SKILL ALIASES (Variations/Synonyms)
    # ================================================================
    op.create_table(
        'skill_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.String(100), nullable=False, unique=True),
        sa.Column('language', sa.String(5), default='id'),
        sa.Column('alias_type', sa.Enum('synonym', 'abbreviation', 'translation', 'variation', name='alias_type_enum'), default='synonym'),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    op.create_index('idx_skill_id', 'skill_aliases', ['skill_id'])
    op.create_index('idx_alias', 'skill_aliases', ['alias'])
    
    # ================================================================
    # 4. VALIDATION HISTORY (Audit Trail)
    # ================================================================
    op.create_table(
        'skill_validation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('validator_user', sa.String(100), nullable=True),
        sa.Column('action', sa.Enum('created', 'approved', 'rejected', 'updated', 'merged', 'deleted', name='validation_action_enum'), nullable=False),
        sa.Column('old_category_id', sa.Integer(), nullable=True),
        sa.Column('new_category_id', sa.Integer(), nullable=True),
        sa.Column('old_status', sa.String(20), nullable=True),
        sa.Column('new_status', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    op.create_index('idx_history_skill', 'skill_validation_history', ['skill_id'])
    op.create_index('idx_history_validator', 'skill_validation_history', ['validator_user'])
    op.create_index('idx_history_action', 'skill_validation_history', ['action'])
    op.create_index('idx_history_created', 'skill_validation_history', ['created_at'])
    
    # ================================================================
    # 5. VALIDATION QUEUE (Skills to Review)
    # ================================================================
    op.create_table(
        'validation_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(100), nullable=False),
        sa.Column('source_count', sa.Integer(), default=1),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'skipped', name='queue_status_enum'), default='pending'),
        sa.Column('assigned_to', sa.String(100), nullable=True),
        sa.Column('suggested_category_id', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('context_sample', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    op.create_index('idx_queue_skill_name', 'validation_queue', ['skill_name'])
    op.create_index('idx_queue_status', 'validation_queue', ['status'])
    op.create_index('idx_queue_priority', 'validation_queue', ['priority'])
    op.create_index('idx_queue_assigned', 'validation_queue', ['assigned_to'])
    
    print("✅ Created 5 skill validation tables (no foreign keys)")


def downgrade():
    """Drop skill validation tables"""
    
    # Drop in reverse order
    op.drop_table('validation_queue')
    op.drop_table('skill_validation_history')
    op.drop_table('skill_aliases')
    op.drop_table('skills_dictionary')
    op.drop_table('skill_categories')
    
    # Drop enums (MySQL)
    op.execute("DROP TYPE IF EXISTS validation_status_enum")
    op.execute("DROP TYPE IF EXISTS alias_type_enum")
    op.execute("DROP TYPE IF EXISTS validation_action_enum")
    op.execute("DROP TYPE IF EXISTS queue_status_enum")
    
    print("✅ Dropped all skill validation tables")