"""Add cache_entries table only

Revision ID: 3644060ecab9
Revises: 7269421e0ef3
Create Date: 2025-09-27 10:54:58.395137

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3644060ecab9"
down_revision: Union[str, Sequence[str], None] = "7269421e0ef3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create cache_entries table
    op.create_table(
        "cache_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cache_key", sa.String(length=255), nullable=False),
        sa.Column("cache_value", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cache_entries_cache_key"), "cache_entries", ["cache_key"], unique=True
    )
    op.create_index(
        op.f("ix_cache_entries_expires_at"),
        "cache_entries",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_cache_entries_expires_at"), table_name="cache_entries")
    op.drop_index(op.f("ix_cache_entries_cache_key"), table_name="cache_entries")
    op.drop_table("cache_entries")
