"""create annotation_types table

Revision ID: 002
Revises: 001
Create Date: 2025-12-11 10:05:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotation_types table"""
    op.create_table(
        'annotation_types',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True, comment='Type code (e.g., NER, SKILL, SENTIMENT)'),
        sa.Column('name', sa.String(100), nullable=False, comment='Display name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Type description'),
        sa.Column('category', sa.String(50), nullable=True, index=True, comment='Category: NLP, Classification, Extraction, etc'),
        sa.Column('entity_field', sa.String(100), nullable=True, comment='Related job field (e.g., judul, deskripsi_singkat)'),
        sa.Column('allows_multiple', sa.Boolean(), default=True, comment='Allow multiple annotations of this type'),
        sa.Column('requires_validation', sa.Boolean(), default=False, comment='Requires manual validation'),
        sa.Column('is_active', sa.Boolean(), default=True, index=True, comment='Active status'),
        sa.Column('display_order', sa.Integer(), default=0, comment='Display order in UI'),
        sa.Column('color_code', sa.String(7), nullable=True, comment='Color for UI display (hex)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotation_types_category', 'annotation_types', ['category', 'is_active'])


def downgrade() -> None:
    """Drop annotation_types table"""
    op.drop_index('idx_annotation_types_category', 'annotation_types')
    op.drop_table('annotation_types')
