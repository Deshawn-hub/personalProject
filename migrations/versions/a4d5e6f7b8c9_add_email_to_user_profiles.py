"""Add email to user profiles

Revision ID: a4d5e6f7b8c9
Revises: 6b8c3f5d9a21
Create Date: 2026-04-05 17:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4d5e6f7b8c9'
down_revision = '6b8c3f5d9a21'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_profiles', sa.Column('email', sa.String(length=120), nullable=False))
    op.create_unique_constraint('uq_user_profiles_email', 'user_profiles', ['email'])


def downgrade():
    op.drop_constraint('uq_user_profiles_email', 'user_profiles', type_='unique')
    op.drop_column('user_profiles', 'email')
