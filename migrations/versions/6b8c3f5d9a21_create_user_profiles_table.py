"""Create user profiles table

Revision ID: 6b8c3f5d9a21
Revises: 4562deae6a28
Create Date: 2026-04-05 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b8c3f5d9a21'
down_revision = '4562deae6a28'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=80), nullable=False),
        sa.Column('last_name', sa.String(length=80), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )


def downgrade():
    op.drop_table('user_profiles')
