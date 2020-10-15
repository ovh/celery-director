"""Add users table

Revision ID: 3f8466b16023
Revises: 05cf96d6fcae
Create Date: 2020-07-15 16:45:02.209593

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils.types import UUIDType


# revision identifiers, used by Alembic.
revision = "3f8466b16023"
down_revision = "05cf96d6fcae"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", UUIDType(binary=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_users_created_at"), table_name="users")
    op.drop_table("users")
