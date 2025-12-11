"""create annotation_quality table

Revision ID: 009
Revises: 008
Create Date: 2025-12-11 10:40:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create annotation_quality table"""
    op.create_table(
        'annotation_quality',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('annotation_id', sa.Integer(), nullable=False, index=True, comment='Reference to annotations table'),
        sa.Column('job_id', sa.Integer(), nullable=False, index=True, comment='Reference to jobs table'),
        sa.Column('annotator_id', sa.Integer(), nullable=True, index=True, comment='Annotator being evaluated'),
        
        # Quality scores
        sa.Column('accuracy_score', sa.Numeric(5, 4), nullable=True, comment='Accuracy score (0-1)'),
        sa.Column('consistency_score', sa.Numeric(5, 4), nullable=True, comment='Consistency with other annotations'),
        sa.Column('completeness_score', sa.Numeric(5, 4), nullable=True, comment='How complete the annotation is'),
        sa.Column('relevance_score', sa.Numeric(5, 4), nullable=True, comment='Relevance of annotation'),
        sa.Column('overall_quality', sa.Numeric(5, 4), nullable=True, comment='Overall quality score'),
        
        # Inter-annotator agreement
        sa.Column('agreement_count', sa.Integer(), default=0, comment='Number of annotators in agreement'),
        sa.Column('disagreement_count', sa.Integer(), default=0, comment='Number of annotators in disagreement'),
        sa.Column('kappa_score', sa.Numeric(5, 4), nullable=True, comment='Cohen Kappa score'),
        
        # Validation details
        sa.Column('is_gold_standard', sa.Boolean(), default=False, comment='Marked as gold standard'),
        sa.Column('validated_by_count', sa.Integer(), default=0, comment='Number of validators'),
        sa.Column('consensus_reached', sa.Boolean(), default=False, comment='Whether consensus was reached'),
        
        # Issues and flags
        sa.Column('has_issues', sa.Boolean(), default=False, index=True, comment='Has quality issues'),
        sa.Column('issue_types', sa.JSON(), nullable=True, comment='List of issue types'),
        sa.Column('issue_description', sa.Text(), nullable=True, comment='Description of issues'),
        sa.Column('needs_review', sa.Boolean(), default=False, index=True, comment='Needs manual review'),
        
        # Feedback
        sa.Column('feedback', sa.Text(), nullable=True, comment='Quality feedback'),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True, comment='Suggestions for improvement'),
        
        # Metadata
        sa.Column('evaluated_by', sa.Integer(), nullable=True, comment='Who evaluated this'),
        sa.Column('evaluation_method', sa.Enum('manual', 'auto', 'peer_review', name='evaluation_method'), default='manual'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Additional quality metrics'),
        
        # Timestamps
        sa.Column('evaluated_at', sa.DateTime(), nullable=True, comment='When evaluation was done'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        
        # sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        # sa.ForeignKeyConstraint(['annotator_id'], ['annotators.id'], ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes
    op.create_index('idx_annotation_quality_scores', 'annotation_quality', ['overall_quality', 'accuracy_score'])
    op.create_index('idx_annotation_quality_issues', 'annotation_quality', ['has_issues', 'needs_review'])
    op.create_index('idx_annotation_quality_annotator', 'annotation_quality', ['annotator_id', 'overall_quality'])
    op.create_index('idx_annotation_quality_gold', 'annotation_quality', ['is_gold_standard'])


def downgrade() -> None:
    """Drop annotation_quality table"""
    op.drop_index('idx_annotation_quality_gold', 'annotation_quality')
    op.drop_index('idx_annotation_quality_annotator', 'annotation_quality')
    op.drop_index('idx_annotation_quality_issues', 'annotation_quality')
    op.drop_index('idx_annotation_quality_scores', 'annotation_quality')
    op.drop_table('annotation_quality')
    op.execute('DROP TYPE IF EXISTS evaluation_method')
