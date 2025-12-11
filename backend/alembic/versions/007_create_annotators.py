"""create annotators table

Revision ID: 007
Revises: 006
Create Date: 2025-12-11 10:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotators table"""
    op.create_table(
        'annotators',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True, comment='Username'),
        sa.Column('email', sa.String(255), nullable=True, unique=True, comment='Email address'),
        sa.Column('full_name', sa.String(255), nullable=True, comment='Full name'),
        
        # Annotator type
        sa.Column('annotator_type', sa.Enum('human', 'ai_model', 'rule_engine', 'hybrid', name='annotator_type'), nullable=False, default='human', index=True),
        sa.Column('model_version', sa.String(100), nullable=True, comment='AI model version if applicable'),
        
        # Permissions and roles
        sa.Column('role', sa.Enum('annotator', 'validator', 'admin', 'system', name='annotator_role'), nullable=False, default='annotator', index=True),
        sa.Column('can_validate', sa.Boolean(), default=False, comment='Can validate others annotations'),
        sa.Column('can_create_labels', sa.Boolean(), default=False, comment='Can create new labels'),
        sa.Column('allowed_annotation_types', sa.JSON(), nullable=True, comment='List of allowed annotation type IDs'),
        
        # Statistics
        sa.Column('total_annotations', sa.Integer(), default=0, comment='Total annotations created'),
        sa.Column('validated_annotations', sa.Integer(), default=0, comment='Annotations validated'),
        sa.Column('rejected_annotations', sa.Integer(), default=0, comment='Annotations rejected'),
        sa.Column('avg_confidence', sa.Numeric(5, 4), nullable=True, comment='Average confidence score'),
        sa.Column('agreement_score', sa.Numeric(5, 4), nullable=True, comment='Inter-annotator agreement'),
        
        # Activity tracking
        sa.Column('last_login_at', sa.DateTime(), nullable=True, comment='Last login time'),
        sa.Column('last_annotation_at', sa.DateTime(), nullable=True, comment='Last annotation time'),
        
        # Status
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('notes', sa.Text(), nullable=True, comment='Admin notes'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotators_type_role', 'annotators', ['annotator_type', 'role'])
    op.create_index('idx_annotators_stats', 'annotators', ['total_annotations', 'agreement_score'])


def downgrade() -> None:
    """Drop annotators table"""
    op.drop_index('idx_annotators_stats', 'annotators')
    op.drop_index('idx_annotators_type_role', 'annotators')
    op.drop_table('annotators')
    op.execute('DROP TYPE IF EXISTS annotator_type')
    op.execute('DROP TYPE IF EXISTS annotator_role')
