"""add origin column to jobs table

Revision ID: a1b2c3d4e5f6
Revises: 99722ec6b2d6
Create Date: 2026-08-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '99722ec6b2d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add origin column to jobs table with default 'api' and backfill from api_keys."""
    # Add the column with a server default first
    op.add_column('jobs', sa.Column('origin', sa.String(16), nullable=False, server_default='api'))

    # Backfill existing rows: set origin='web' for jobs created with web_ session keys
    op.execute("""
        UPDATE jobs
        SET origin = 'web'
        WHERE api_key_id IN (
            SELECT id FROM api_keys WHERE key_prefix LIKE 'web_%'
        )
    """)

    # Remove the server default after backfill (new rows get origin from application code)
    op.alter_column('jobs', 'origin', server_default=None)

    # Add index for efficient filtering
    op.create_index('ix_jobs_origin', 'jobs', ['origin'])


def downgrade() -> None:
    """Remove origin column and its index from jobs table."""
    op.drop_index('ix_jobs_origin', table_name='jobs')
    op.drop_column('jobs', 'origin')
