"""create annotations table

Revision ID: 003
Revises: 002
Create Date: 2025-12-11 10:10:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotations table"""
    op.create_table(
        'annotations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        
        # Relationships
        sa.Column('job_id', sa.Integer(), nullable=False, index=True, comment='Reference to jobs table'),
        sa.Column('annotation_type_id', sa.Integer(), nullable=False, index=True, comment='Reference to annotation_types'),
        sa.Column('annotator_id', sa.Integer(), nullable=True, index=True, comment='Who created this annotation'),
        
        # Annotation content
        sa.Column('field_name', sa.String(100), nullable=True, comment='Which field is annotated (e.g., judul, deskripsi_singkat)'),
        sa.Column('original_text', sa.Text(), nullable=True, comment='Original text being annotated'),
        sa.Column('start_offset', sa.Integer(), nullable=True, comment='Start position in text'),
        sa.Column('end_offset', sa.Integer(), nullable=True, comment='End position in text'),
        sa.Column('annotated_text', sa.Text(), nullable=True, comment='Extracted/highlighted text'),
        
        # Label and value
        sa.Column('label', sa.String(255), nullable=True, index=True, comment='Annotation label'),
        sa.Column('value', sa.Text(), nullable=True, comment='Annotation value (JSON or text)'),
        sa.Column('confidence_score', sa.Numeric(5, 4), nullable=True, comment='Confidence score (0-1) for auto-annotations'),
        
        # Metadata
        sa.Column('method', sa.Enum('manual', 'auto', 'semi_auto', name='annotation_method'), default='manual', comment='How annotation was created'),
        sa.Column('source', sa.String(100), nullable=True, comment='Source of annotation (model name, rule name, etc)'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Additional metadata as JSON'),
        
        # Status and validation
        sa.Column('status', sa.Enum('pending', 'validated', 'rejected', 'in_review', name='annotation_status'), default='pending', index=True),
        sa.Column('is_validated', sa.Boolean(), default=False, index=True, comment='Validation status'),
        sa.Column('validated_by', sa.Integer(), nullable=True, comment='Validator user ID'),
        sa.Column('validated_at', sa.DateTime(), nullable=True, comment='Validation timestamp'),
        sa.Column('validation_notes', sa.Text(), nullable=True, comment='Validation notes'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # Foreign keys
        # sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['annotation_type_id'], ['annotation_types.id'], ondelete='RESTRICT'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotations_job_type', 'annotations', ['job_id', 'annotation_type_id'])
    op.create_index('idx_annotations_label', 'annotations', ['annotation_type_id', 'label'])
    op.create_index('idx_annotations_method_status', 'annotations', ['method', 'status'])
    op.create_index('idx_annotations_created', 'annotations', ['created_at'])


def downgrade() -> None:
    """Drop annotations table"""
    op.drop_index('idx_annotations_created', 'annotations')
    op.drop_index('idx_annotations_method_status', 'annotations')
    op.drop_index('idx_annotations_label', 'annotations')
    op.drop_index('idx_annotations_job_type', 'annotations')
    op.drop_table('annotations')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS annotation_method')
    op.execute('DROP TYPE IF EXISTS annotation_status')
