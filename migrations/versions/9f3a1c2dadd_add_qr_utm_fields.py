"""add qr utm fields

Revision ID: 9f3a1c2dadd
Revises: c8b9e2a1f3c4
Create Date: 2025-12-02 04:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f3a1c2dadd'
down_revision = 'c8b9e2a1f3c4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('qr_codes') as batch_op:
        batch_op.add_column(sa.Column('utm_source', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('utm_medium', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('utm_campaign', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('utm_term', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('utm_content', sa.String(length=64), nullable=True))


def downgrade():
    with op.batch_alter_table('qr_codes') as batch_op:
        batch_op.drop_column('utm_content')
        batch_op.drop_column('utm_term')
        batch_op.drop_column('utm_campaign')
        batch_op.drop_column('utm_medium')
        batch_op.drop_column('utm_source')
