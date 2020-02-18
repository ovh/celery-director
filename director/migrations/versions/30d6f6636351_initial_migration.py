"""Initial migration

Revision ID: 30d6f6636351
Revises: 
Create Date: 2020-02-07 18:34:41.680883

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils.types import UUIDType

from director.models.utils import JSONBType


# revision identifiers, used by Alembic.
revision = "30d6f6636351"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workflows",
        sa.Column("id", UUIDType(binary=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("project", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "progress", "success", "error", "canceled", name="statustype"
            ),
            nullable=False,
        ),
        sa.Column("payload", JSONBType(), nullable=True),
        sa.Column("periodic", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflows")),
    )
    op.create_index(
        op.f("ix_workflows_created_at"), "workflows", ["created_at"], unique=False
    )

    op.create_table(
        "tasks",
        sa.Column("id", UUIDType(binary=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "progress", "success", "error", "canceled", name="statustype"
            ),
            nullable=False,
        ),
        sa.Column("previous", JSONBType(), nullable=True),
        sa.Column("workflow_id", UUIDType(binary=False), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
            name=op.f("fk_tasks_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
    )
    op.create_index(op.f("ix_tasks_created_at"), "tasks", ["created_at"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_tasks_created_at"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_workflows_created_at"), table_name="workflows")
    op.drop_table("workflows")
