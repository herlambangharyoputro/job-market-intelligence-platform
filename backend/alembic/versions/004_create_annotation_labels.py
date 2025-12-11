"""create annotation_labels table

Revision ID: 004
Revises: 003
Create Date: 2025-12-11 10:15:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotation_labels table"""
    op.create_table(
        'annotation_labels',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('annotation_type_id', sa.Integer(), nullable=False, index=True, comment='Reference to annotation_types'),
        sa.Column('label_code', sa.String(100), nullable=False, comment='Label code (e.g., SKILL_PYTHON, LOC_JAKARTA)'),
        sa.Column('label_name', sa.String(255), nullable=False, comment='Display name'),
        sa.Column('label_name_en', sa.String(255), nullable=True, comment='English name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Label description'),
        sa.Column('parent_label_id', sa.Integer(), nullable=True, index=True, comment='Parent label for hierarchy'),
        sa.Column('level', sa.Integer(), default=0, comment='Hierarchy level'),
        sa.Column('synonyms', sa.JSON(), nullable=True, comment='List of synonyms'),
        sa.Column('examples', sa.JSON(), nullable=True, comment='Example texts'),
        sa.Column('color_code', sa.String(7), nullable=True, comment='Color for UI display'),
        sa.Column('icon', sa.String(50), nullable=True, comment='Icon identifier'),
        sa.Column('usage_count', sa.Integer(), default=0, comment='How many times used'),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # sa.ForeignKeyConstraint(['annotation_type_id'], ['annotation_types.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['parent_label_id'], ['annotation_labels.id'], ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotation_labels_type_code', 'annotation_labels', ['annotation_type_id', 'label_code'], unique=True)
    op.create_index('idx_annotation_labels_parent', 'annotation_labels', ['parent_label_id', 'level'])
    op.create_index('idx_annotation_labels_usage', 'annotation_labels', ['usage_count'])


def downgrade() -> None:
    """Drop annotation_labels table"""
    op.drop_index('idx_annotation_labels_usage', 'annotation_labels')
    op.drop_index('idx_annotation_labels_parent', 'annotation_labels')
    op.drop_index('idx_annotation_labels_type_code', 'annotation_labels')
    op.drop_table('annotation_labels')
