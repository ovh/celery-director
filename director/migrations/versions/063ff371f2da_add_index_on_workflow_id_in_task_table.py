"""Add index on workflow_id in task table

Revision ID: 063ff371f2da
Revises: 3f8466b16023
Create Date: 2020-10-09 12:09:27.596429

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "063ff371f2da"
down_revision = "3f8466b16023"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        op.f("ix_tasks_workflow_id"), "tasks", ["workflow_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_tasks_workflow_id"), table_name="tasks")
