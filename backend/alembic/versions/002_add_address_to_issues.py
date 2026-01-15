"""add address column to issues

Revision ID: 002_add_address
Revises: 001_initial_schema
Create Date: 2026-01-14
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_add_address"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("issues", sa.Column("address", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("issues", "address")
