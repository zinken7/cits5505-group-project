"""add is_root to users

Revision ID: c1a2b3c4d5e6
Revises: fef786799b08
Create Date: 2026-04-27

"""
from alembic import op
import sqlalchemy as sa


revision = "c1a2b3c4d5e6"
down_revision = "fef786799b08"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("is_root", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("is_root")
