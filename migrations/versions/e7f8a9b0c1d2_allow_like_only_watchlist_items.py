"""allow like-only watchlist items

Revision ID: e7f8a9b0c1d2
Revises: d4e5f6a7b8c9
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa


revision = "e7f8a9b0c1d2"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("watchlist_items", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=20),
            nullable=True,
            existing_server_default=None,
        )


def downgrade():
    op.execute("UPDATE watchlist_items SET status = 'planned' WHERE status IS NULL")
    with op.batch_alter_table("watchlist_items", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(length=20),
            nullable=False,
            existing_server_default=None,
        )
