"""add indexes for qr tables

Revision ID: d1e2f3a4b5c6
Revises: c8b9e2a1f3c4
Create Date: 2025-12-02 19:48:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = '9f3a1c2dadd'
branch_labels = None
depends_on = None


def upgrade():
    """Create explicit indexes to improve common query patterns.

    Guarded to avoid failures if indexes were already created (e.g., via
    prior migrations or Column(index=True) flags).
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    def existing_index_names(table: str) -> set[str]:
        try:
            return {ix['name'] for ix in inspector.get_indexes(table)}
        except Exception:
            return set()

    def create_index_if_missing(name: str, table: str, columns: list[str]):
        if name not in existing_index_names(table):
            op.create_index(name, table, columns)

    # qr_scans
    create_index_if_missing('ix_qr_scans_qr_id', 'qr_scans', ['qr_id'])
    create_index_if_missing('ix_qr_scans_ts', 'qr_scans', ['ts'])

    # qr_codes
    create_index_if_missing('ix_qr_codes_user_id', 'qr_codes', ['user_id'])
    create_index_if_missing('ix_qr_codes_created_at', 'qr_codes', ['created_at'])


def downgrade():
    """Drop indexes if they exist."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    def existing_index_names(table: str) -> set[str]:
        try:
            return {ix['name'] for ix in inspector.get_indexes(table)}
        except Exception:
            return set()

    def drop_index_if_exists(name: str, table: str):
        if name in existing_index_names(table):
            op.drop_index(name, table_name=table)

    # qr_scans
    drop_index_if_exists('ix_qr_scans_qr_id', 'qr_scans')
    drop_index_if_exists('ix_qr_scans_ts', 'qr_scans')

    # qr_codes
    drop_index_if_exists('ix_qr_codes_user_id', 'qr_codes')
    drop_index_if_exists('ix_qr_codes_created_at', 'qr_codes')
