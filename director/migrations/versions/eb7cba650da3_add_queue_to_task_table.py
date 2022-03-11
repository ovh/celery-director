"""Add queue to task table

Revision ID: eb7cba650da3
Revises: 46e4acde004e
Create Date: 2022-03-10 13:09:20.21090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb7cba650da3"
down_revision = "46e4acde004e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("queue", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("tasks", "queue")
