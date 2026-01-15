"""Initial schema with issues and issue_events tables

Revision ID: 001
Revises: 
Create Date: 2026-01-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create issues table
    op.create_table(
        'issues',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('report_images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('thread_id', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('priority_score', sa.Integer(), nullable=True),
        sa.Column('needs_clarification', sa.Boolean(), nullable=True),
        sa.Column('clarification', sa.String(), nullable=True),
        sa.Column('number_of_matches', sa.Integer(), nullable=False),
        sa.Column('creation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create issue_events table
    op.create_table(
        'issue_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('creation_time', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['issues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('issue_events')
    op.drop_table('issues')
