"""create qr tables

Revision ID: c8b9e2a1f3c4
Revises: 7b2c3df0a9d3
Create Date: 2025-12-02 10:59:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8b9e2a1f3c4'
down_revision = '7b2c3df0a9d3'
branch_labels = None
depends_on = None


def upgrade():
    # Create qr_codes table (without UTM columns; added later by 9f3a1c2dadd)
    op.create_table(
        'qr_codes',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('qr_type', sa.String(length=30), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=32), unique=True, nullable=True),
        sa.Column('is_trackable', sa.Boolean(), server_default=sa.text('1'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scan_count', sa.Integer(), server_default=sa.text('0'), nullable=True),
        sa.Column('last_scan_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create qr_scans table (includes UTM columns as per model)
    op.create_table(
        'qr_scans',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('qr_id', sa.Integer(), sa.ForeignKey('qr_codes.id'), nullable=False, index=True),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('country', sa.String(length=64), nullable=True),
        sa.Column('region', sa.String(length=64), nullable=True),
        sa.Column('city', sa.String(length=64), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('ua_raw', sa.Text(), nullable=True),
        sa.Column('device_type', sa.String(length=16), nullable=True),
        sa.Column('os', sa.String(length=32), nullable=True),
        sa.Column('browser', sa.String(length=32), nullable=True),
        sa.Column('referrer', sa.Text(), nullable=True),
        sa.Column('utm_source', sa.String(length=64), nullable=True),
        sa.Column('utm_medium', sa.String(length=64), nullable=True),
        sa.Column('utm_campaign', sa.String(length=64), nullable=True),
        sa.Column('utm_term', sa.String(length=64), nullable=True),
        sa.Column('utm_content', sa.String(length=64), nullable=True),
    )


def downgrade():
    op.drop_table('qr_scans')
    op.drop_table('qr_codes')
