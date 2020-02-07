"""Fix constraints

Revision ID: 2e4550411ff1
Revises: 70631f8bcff3
Create Date: 2020-02-06 16:22:14.328572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2e4550411ff1"
down_revision = "70631f8bcff3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_constraint("tasks_workflow_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "tasks_workflow_id_fkey", "workflows", ["workflow_id"], ["id"]
        )


def downgrade():
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_constraint("tasks_workflow_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "tasks_workflow_id_fkey", "tasks", ["workflow_id"], ["id"]
        )
