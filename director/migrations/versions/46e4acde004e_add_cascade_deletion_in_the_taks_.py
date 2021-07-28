"""Add cascade deletion in the taks model for workflow deletion

Revision ID: 46e4acde004e
Revises: 2ac615d6850b
Create Date: 2021-07-16 11:54:27.946028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "46e4acde004e"
down_revision = "2ac615d6850b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("fk_tasks_workflow_id_workflows", "tasks", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_tasks_workflow_id_workflows"),
        "tasks",
        "workflows",
        ["workflow_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_tasks_workflow_id_workflows"), "tasks", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_tasks_workflow_id_workflows", "tasks", "workflows", ["workflow_id"], ["id"]
    )
