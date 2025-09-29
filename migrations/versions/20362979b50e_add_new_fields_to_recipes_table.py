"""Add new fields to recipes table

Revision ID: 20362979b50e
Revises: b2ff1e9593f6
Create Date: 2025-09-24 12:14:19.291736

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20362979b50e"
down_revision: Union[str, Sequence[str], None] = "b2ff1e9593f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to recipes table
    op.add_column(
        "recipes", sa.Column("difficulty", sa.String(length=20), nullable=True)
    )
    op.add_column("recipes", sa.Column("cuisine", sa.String(length=100), nullable=True))
    op.add_column("recipes", sa.Column("tags", sa.JSON(), nullable=True))

    # Change instructions column from TEXT to JSON
    op.execute(
        "ALTER TABLE recipes ALTER COLUMN instructions TYPE JSON USING instructions::json"
    )

    # Drop the old category column
    op.drop_column("recipes", "category")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert changes
    op.add_column(
        "recipes", sa.Column("category", sa.String(length=100), nullable=True)
    )
    op.execute(
        "ALTER TABLE recipes ALTER COLUMN instructions TYPE TEXT USING instructions::text"
    )
    op.drop_column("recipes", "tags")
    op.drop_column("recipes", "cuisine")
    op.drop_column("recipes", "difficulty")
