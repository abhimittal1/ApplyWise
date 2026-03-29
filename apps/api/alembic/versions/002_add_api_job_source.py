"""add API to JobSource enum

Revision ID: 002
Revises: 001
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE jobsource ADD VALUE IF NOT EXISTS 'API'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values directly
    pass
