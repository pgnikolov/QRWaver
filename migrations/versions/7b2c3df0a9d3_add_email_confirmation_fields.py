"""add email confirmation fields

Revision ID: 7b2c3df0a9d3
Revises: 423c21b1ff06
Create Date: 2025-12-01 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Boolean


# revision identifiers, used by Alembic.
revision = '7b2c3df0a9d3'
down_revision = '423c21b1ff06'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Determine current columns in 'users'
    existing_cols = {col['name'] for col in inspector.get_columns('users')}

    # Add new columns to users table if they don't already exist
    if 'is_verified' not in existing_cols:
        op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'confirm_token_hash' not in existing_cols:
        op.add_column('users', sa.Column('confirm_token_hash', sa.String(length=255), nullable=True))
    if 'confirm_expires_at' not in existing_cols:
        op.add_column('users', sa.Column('confirm_expires_at', sa.DateTime(timezone=True), nullable=True))
    if 'confirm_sent_at' not in existing_cols:
        op.add_column('users', sa.Column('confirm_sent_at', sa.DateTime(timezone=True), nullable=True))

    # Refresh columns after potential additions
    existing_cols = {col['name'] for col in inspector.get_columns('users')}

    # For existing users, consider them verified to avoid locking out legacy accounts
    if 'is_verified' in existing_cols:
        users = table('users', column('is_verified', Boolean))
        op.execute(users.update().values(is_verified=True))

    # Remove server_default for future inserts to rely on ORM default.
    # SQLite doesn't support ALTER COLUMN DROP DEFAULT; skip for sqlite.
    if bind.dialect.name != "sqlite" and 'is_verified' in existing_cols:
        op.alter_column('users', 'is_verified', server_default=None)


def downgrade():
    # Drop columns if they exist (guards for partially applied migrations)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = {col['name'] for col in inspector.get_columns('users')}

    if 'confirm_sent_at' in existing_cols:
        op.drop_column('users', 'confirm_sent_at')
    if 'confirm_expires_at' in existing_cols:
        op.drop_column('users', 'confirm_expires_at')
    if 'confirm_token_hash' in existing_cols:
        op.drop_column('users', 'confirm_token_hash')
    if 'is_verified' in existing_cols:
        op.drop_column('users', 'is_verified')
