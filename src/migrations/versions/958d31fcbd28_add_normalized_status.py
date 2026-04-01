"""add normalized status

Revision ID: 958d31fcbd28
Revises: 585aa228569c
Create Date: 2026-03-29 11:25:14.622730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '958d31fcbd28'
down_revision: Union[str, Sequence[str], None] = '585aa228569c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE document_status ADD VALUE 'NORMALIZED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
