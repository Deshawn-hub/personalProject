"""Expand user profile password column

Revision ID: b1c2d3e4f5a6
Revises: a4d5e6f7b8c9
Create Date: 2026-04-05 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'a4d5e6f7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'user_profiles',
        'password',
        existing_type=sa.String(length=128),
        type_=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        'user_profiles',
        'password',
        existing_type=sa.String(length=255),
        type_=sa.String(length=128),
        existing_nullable=False,
    )
