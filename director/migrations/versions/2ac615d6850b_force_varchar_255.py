"""Force varchar 255

Revision ID: 2ac615d6850b
Revises: 063ff371f2da
Create Date: 2020-10-09 17:35:12.402690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ac615d6850b"
down_revision = "063ff371f2da"
branch_labels = None
depends_on = None


def upgrade():
    """
    This migration is only useful for an existing Celery Director instance.
    """
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.alter_column(
            "key",
            existing_type=sa.VARCHAR(),
            type_=sa.String(length=255),
            existing_nullable=False,
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.VARCHAR(),
            type_=sa.String(length=255),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "username",
            existing_type=sa.VARCHAR(),
            type_=sa.String(length=255),
            existing_nullable=False,
        )

    with op.batch_alter_table("workflows") as batch_op:
        batch_op.alter_column(
            "name",
            existing_type=sa.VARCHAR(),
            type_=sa.String(length=255),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "project",
            existing_type=sa.VARCHAR(),
            type_=sa.String(length=255),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("workflows") as batch_op:
        batch_op.alter_column(
            "project",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "name",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "username",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )

    with op.batch_alter_table("tasks") as batch_op:
        batch_op.alter_column(
            "key",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )
