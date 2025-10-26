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
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE users SET hashed_password = :default WHERE hashed_password IS NULL"
        ),
        {"default": DEFAULT_HASHED_PASSWORD},
    )

    op.alter_column(
        "users",
        "first_name",
        server_default=None,
        existing_type=sa.String(),
    )
    op.alter_column(
        "users",
        "last_name",
        server_default=None,
        existing_type=sa.String(),
    )
    op.alter_column(
        "users",
        "phone",
        server_default=None,
        existing_type=sa.String(),
    )
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("users", "phone")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(),
        nullable=True,
    )
