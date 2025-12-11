"""create annotation_history table

Revision ID: 006
Revises: 005
Create Date: 2025-12-11 10:25:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotation_history table"""
    op.create_table(
        'annotation_history',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('annotation_id', sa.Integer(), nullable=False, index=True, comment='Reference to annotations table'),
        sa.Column('action', sa.Enum('create', 'update', 'delete', 'validate', 'reject', name='history_action'), nullable=False, index=True),
        sa.Column('changed_by', sa.Integer(), nullable=True, index=True, comment='User who made the change'),
        
        # Change details
        sa.Column('field_changed', sa.String(100), nullable=True, comment='Which field was changed'),
        sa.Column('old_value', sa.Text(), nullable=True, comment='Previous value'),
        sa.Column('new_value', sa.Text(), nullable=True, comment='New value'),
        sa.Column('change_reason', sa.Text(), nullable=True, comment='Reason for change'),
        
        # Metadata
        sa.Column('ip_address', sa.String(45), nullable=True, comment='IP address of user'),
        sa.Column('user_agent', sa.String(500), nullable=True, comment='Browser user agent'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Additional metadata'),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), index=True),
        
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ondelete='CASCADE'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotation_history_annotation_action', 'annotation_history', ['annotation_id', 'action'])
    op.create_index('idx_annotation_history_user', 'annotation_history', ['changed_by', 'created_at'])


def downgrade() -> None:
    """Drop annotation_history table"""
    op.drop_index('idx_annotation_history_user', 'annotation_history')
    op.drop_index('idx_annotation_history_annotation_action', 'annotation_history')
    op.drop_table('annotation_history')
    op.execute('DROP TYPE IF EXISTS history_action')
