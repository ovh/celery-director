"""Add cascade in task model for workflow deletion

Revision ID: 46e4acde004e
Revises: 2ac615d6850b
Create Date: 2021-07-16 11:54:27.946028

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "46e4acde004e"
down_revision = "2ac615d6850b"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.engine.name == "sqlite":
        # SQLite does not support to alter constraints on existing tables.
        # Batch mode is used to copy data to a temporary table meanwhile creating a brand new
        # table with the required constraint.
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.drop_constraint(
                op.f("fk_tasks_workflow_id_workflows"), type_="foreignkey"
            )
            batch_op.create_foreign_key(
                op.f("fk_tasks_workflow_id_workflows"),
                "workflows",
                ["workflow_id"],
                ["id"],
                ondelete="cascade",
            )
        return

    op.drop_constraint(
        op.f("fk_tasks_workflow_id_workflows"), "tasks", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_tasks_workflow_id_workflows"),
        "tasks",
        "workflows",
        ["workflow_id"],
        ["id"],
        ondelete="cascade",
    )


def downgrade():
    bind = op.get_bind()
    if bind.engine.name == "sqlite":
        with op.batch_alter_table("tasks") as batch_op:
            batch_op.drop_constraint(
                op.f("fk_tasks_workflow_id_workflows"), type_="foreignkey"
            )
            batch_op.create_foreign_key(
                op.f("fk_tasks_workflow_id_workflows"),
                "workflows",
                ["workflow_id"],
                ["id"],
            )
        return

    op.drop_constraint(
        op.f("fk_tasks_workflow_id_workflows"), "tasks", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_tasks_workflow_id_workflows"),
        "tasks",
        "workflows",
        ["workflow_id"],
        ["id"],
    )
