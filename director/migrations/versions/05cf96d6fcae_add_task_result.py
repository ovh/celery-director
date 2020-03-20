"""Add task result

Revision ID: 05cf96d6fcae
Revises: 30d6f6636351
Create Date: 2020-03-20 19:16:48.520652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "05cf96d6fcae"
down_revision = "30d6f6636351"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("result", sa.PickleType(), nullable=True))


def downgrade():
    op.drop_column("tasks", "result")
