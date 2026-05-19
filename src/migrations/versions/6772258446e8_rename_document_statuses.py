"""rename document statuses

Revision ID: 6772258446e8
Revises: 6f2e1ef48d06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6772258446e8'
down_revision: Union[str, Sequence[str], None] = '6f2e1ef48d06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


old_options = (
    'UPLOADED',
    'PROCESSING',
    'NORMALIZED',
    'EMBEDDING',
    'INDEXING',
    'READY',
    'FAILED',
    'DELETED',
)

new_options = (
    'uploaded',
    'processing',
    'normalized',
    'embedding',
    'indexing',
    'ready',
    'failed',
    'deleted',
)


def upgrade() -> None:
    # 1. rename old enum
    op.execute(
        "ALTER TYPE document_status RENAME TO document_status_old"
    )

    # 2. create new enum
    new_enum = sa.Enum(*new_options, name='document_status')
    new_enum.create(op.get_bind())

    # 3. alter column type
    op.execute("""
        ALTER TABLE ingestion_documents
        ALTER COLUMN status
        TYPE document_status
        USING lower(status::text)::document_status
    """)

    # 4. drop old enum
    op.execute("DROP TYPE document_status_old")


def downgrade() -> None:
    # recreate old enum
    old_enum = sa.Enum(*old_options, name='document_status_old')
    old_enum.create(op.get_bind())

    op.execute("""
        ALTER TABLE ingestion_documents
        ALTER COLUMN status
        TYPE document_status_old
        USING upper(status::text)::document_status_old
    """)

    op.execute("DROP TYPE document_status")

    op.execute(
        "ALTER TYPE document_status_old RENAME TO document_status"
    )