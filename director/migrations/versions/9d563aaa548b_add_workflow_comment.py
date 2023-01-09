"""Add workflow comment

Revision ID: 9d563aaa548b
Revises: 9817ccf13cb5
Create Date: 2022-07-26 19:45:40.946254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9d563aaa548b"
down_revision = "9817ccf13cb5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "workflows",
        sa.Column("comment", sa.String(255), nullable=True),
    )


def downgrade():
    op.drop_column("workflows", "comment")
