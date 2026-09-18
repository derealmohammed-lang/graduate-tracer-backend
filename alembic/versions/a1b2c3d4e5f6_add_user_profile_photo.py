"""add user profile_photo column

Revision ID: a1b2c3d4e5f6
Revises: 3f219f79d524
Create Date: 2026-03-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "3f219f79d524"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("profile_photo", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "profile_photo")
