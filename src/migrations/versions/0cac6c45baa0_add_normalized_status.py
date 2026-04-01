"""add normalized status

Revision ID: 0cac6c45baa0
Revises: 958d31fcbd28
Create Date: 2026-03-29 11:26:17.547340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cac6c45baa0'
down_revision: Union[str, Sequence[str], None] = '958d31fcbd28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE document_status ADD VALUE 'NORMALIZED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
