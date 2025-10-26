"""add user profile fields

Revision ID: d4e5f6a7b8c9
Revises: c2d3e4f5a6b7
Create Date: 2025-10-26 03:05:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None

DEFAULT_HASHED_PASSWORD = "$2b$12$eT5RnyrpmLraeJiJ5bmdNeTZxCed.3qzOeSAAq8KHSikiMJP7dqNu"


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("first_name", sa.String(), nullable=False, server_default="Unknown"),
    )
    op.add_column(
        "users",
        sa.Column("last_name", sa.String(), nullable=False, server_default="User"),
    )
    op.add_column(
        "users",
        sa.Column("phone", sa.String(), nullable=False, server_default="0000000000"),
    )
    op.add_column(
        "users",
        sa.Column(
            "hashed_password",
            sa.String(),
            nullable=False,
            server_default=DEFAULT_HASHED_PASSWORD,
        ),
    )

    op.alter_column("users", "first_name", server_default=None)
    op.alter_column("users", "last_name", server_default=None)
    op.alter_column("users", "phone", server_default=None)
    op.alter_column("users", "hashed_password", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "phone")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
