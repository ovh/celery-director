"""Init database

Revision ID: 70631f8bcff3
Revises: 
Create Date: 2019-12-11 12:52:13.012223

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils.types import JSONType, UUIDType

# revision identifiers, used by Alembic.
revision = "70631f8bcff3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
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
        sa.Column("previous", JSONType(), nullable=True),
        sa.Column("workflow_id", UUIDType(binary=False), nullable=False,),
        sa.ForeignKeyConstraint(["workflow_id"], ["tasks.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_created_at"), "tasks", ["created_at"], unique=False)
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
        sa.Column("payload", JSONType(), nullable=True),
        sa.Column("periodic", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_workflows_created_at"), "workflows", ["created_at"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_tasks_created_at"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_workflows_created_at"), table_name="workflows")
    op.drop_table("workflows")
