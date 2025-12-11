"""create annotation_tasks table

Revision ID: 008
Revises: 007
Create Date: 2025-12-11 10:35:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotation_tasks table"""
    op.create_table(
        'annotation_tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('task_name', sa.String(255), nullable=False, comment='Task name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Task description'),
        
        # Task assignment
        sa.Column('assigned_to', sa.Integer(), nullable=True, index=True, comment='Assigned annotator ID'),
        sa.Column('annotation_type_id', sa.Integer(), nullable=False, index=True, comment='Type of annotation required'),
        
        # Task scope
        sa.Column('job_filters', sa.JSON(), nullable=True, comment='Filters to select jobs (e.g., {"level": "Entry", "fungsi": "IT"})'),
        sa.Column('total_jobs', sa.Integer(), default=0, comment='Total jobs to annotate'),
        sa.Column('completed_jobs', sa.Integer(), default=0, comment='Completed annotations'),
        
        # Task settings
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='task_priority'), default='medium', index=True),
        sa.Column('deadline', sa.DateTime(), nullable=True, index=True, comment='Task deadline'),
        sa.Column('instructions', sa.Text(), nullable=True, comment='Specific instructions for annotators'),
        sa.Column('guidelines_url', sa.String(500), nullable=True, comment='Link to annotation guidelines'),
        
        # Requirements
        sa.Column('requires_validation', sa.Boolean(), default=False, comment='Requires validation after annotation'),
        sa.Column('min_annotations_per_job', sa.Integer(), default=1, comment='Minimum annotations per job'),
        sa.Column('require_all_fields', sa.Boolean(), default=False, comment='Must annotate all applicable fields'),
        
        # Status tracking
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'cancelled', 'on_hold', name='task_status'), default='pending', index=True),
        sa.Column('progress_percentage', sa.Numeric(5, 2), default=0, comment='Completion percentage'),
        
        # Timestamps
        sa.Column('started_at', sa.DateTime(), nullable=True, comment='When task was started'),
        sa.Column('completed_at', sa.DateTime(), nullable=True, comment='When task was completed'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        sa.ForeignKeyConstraint(['assigned_to'], ['annotators.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['annotation_type_id'], ['annotation_types.id'], ondelete='RESTRICT'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotation_tasks_assignee_status', 'annotation_tasks', ['assigned_to', 'status'])
    op.create_index('idx_annotation_tasks_deadline', 'annotation_tasks', ['deadline', 'status'])
    op.create_index('idx_annotation_tasks_progress', 'annotation_tasks', ['progress_percentage', 'status'])


def downgrade() -> None:
    """Drop annotation_tasks table"""
    op.drop_index('idx_annotation_tasks_progress', 'annotation_tasks')
    op.drop_index('idx_annotation_tasks_deadline', 'annotation_tasks')
    op.drop_index('idx_annotation_tasks_assignee_status', 'annotation_tasks')
    op.drop_table('annotation_tasks')
    op.execute('DROP TYPE IF EXISTS task_priority')
    op.execute('DROP TYPE IF EXISTS task_status')
