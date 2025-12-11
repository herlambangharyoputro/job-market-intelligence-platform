"""create annotation_rules table

Revision ID: 005
Revises: 004
Create Date: 2025-12-11 10:20:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotation_rules table"""
    op.create_table(
        'annotation_rules',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('annotation_type_id', sa.Integer(), nullable=False, index=True),
        sa.Column('rule_name', sa.String(255), nullable=False, unique=True, comment='Unique rule name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Rule description'),
        
        # Rule definition
        sa.Column('rule_type', sa.Enum('regex', 'keyword', 'ml_model', 'dictionary', 'custom', name='rule_type'), nullable=False, index=True),
        sa.Column('pattern', sa.Text(), nullable=True, comment='Regex pattern or keyword list'),
        sa.Column('model_name', sa.String(255), nullable=True, comment='ML model identifier'),
        sa.Column('dictionary_data', sa.JSON(), nullable=True, comment='Dictionary lookup data'),
        sa.Column('custom_function', sa.String(255), nullable=True, comment='Custom function name'),
        
        # Rule parameters
        sa.Column('parameters', sa.JSON(), nullable=True, comment='Additional parameters as JSON'),
        sa.Column('min_confidence', sa.Numeric(5, 4), default=0.7, comment='Minimum confidence threshold'),
        sa.Column('applies_to_fields', sa.JSON(), nullable=True, comment='List of job fields this rule applies to'),
        
        # Priority and status
        sa.Column('priority', sa.Integer(), default=0, comment='Execution priority (higher first)'),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('run_order', sa.Integer(), default=0, comment='Execution order'),
        
        # Statistics
        sa.Column('execution_count', sa.Integer(), default=0, comment='How many times executed'),
        sa.Column('success_count', sa.Integer(), default=0, comment='Successful annotations'),
        sa.Column('avg_confidence', sa.Numeric(5, 4), nullable=True, comment='Average confidence score'),
        sa.Column('last_executed_at', sa.DateTime(), nullable=True, comment='Last execution time'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # sa.ForeignKeyConstraint(['annotation_type_id'], ['annotation_types.id'], ondelete='CASCADE'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotation_rules_type_active', 'annotation_rules', ['annotation_type_id', 'is_active'])
    op.create_index('idx_annotation_rules_priority', 'annotation_rules', ['priority', 'run_order'])
    op.create_index('idx_annotation_rules_performance', 'annotation_rules', ['execution_count', 'success_count'])


def downgrade() -> None:
    """Drop annotation_rules table"""
    op.drop_index('idx_annotation_rules_performance', 'annotation_rules')
    op.drop_index('idx_annotation_rules_priority', 'annotation_rules')
    op.drop_index('idx_annotation_rules_type_active', 'annotation_rules')
    op.drop_table('annotation_rules')
    op.execute('DROP TYPE IF EXISTS rule_type')
