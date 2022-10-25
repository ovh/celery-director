"""Add is_hook on Task

Revision ID: 9817ccf13cb5
Revises: 46e4acde004e
Create Date: 2022-10-21 15:32:26.186650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9817ccf13cb5"
down_revision = "46e4acde004e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("is_hook", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("tasks", "is_hook")
