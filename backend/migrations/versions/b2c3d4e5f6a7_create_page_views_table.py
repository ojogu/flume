"""create page_views table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-22 10:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create page_views table for analytics tracking."""
    op.create_table(
        'page_views',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('path', sa.Text(), nullable=False),
        sa.Column('visitor_hash', sa.String(64), nullable=False),
        sa.Column('referrer', sa.Text(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_page_views')),
    )
    op.create_index('ix_page_views_path', 'page_views', ['path'])
    op.create_index('ix_page_views_visitor_hash', 'page_views', ['visitor_hash'])
    op.create_index('ix_page_views_created_at', 'page_views', ['created_at'])


def downgrade() -> None:
    """Drop page_views table."""
    op.drop_index('ix_page_views_created_at', table_name='page_views')
    op.drop_index('ix_page_views_visitor_hash', table_name='page_views')
    op.drop_index('ix_page_views_path', table_name='page_views')
    op.drop_table('page_views')
