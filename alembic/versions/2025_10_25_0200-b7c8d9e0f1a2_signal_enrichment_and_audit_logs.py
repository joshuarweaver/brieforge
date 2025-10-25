"""signal_enrichment_and_audit_logs

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-10-25 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add provenance column, signal enrichments, and audit logs tables."""
    # Add provenance column to signals
    op.add_column('signals', sa.Column('provenance', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))

    bind = op.get_bind()

    # Create enum type for enrichment if it does not already exist
    bind.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'signal_enrichment_type') THEN
                    CREATE TYPE signal_enrichment_type AS ENUM ('semantic', 'performance', 'trend');
                END IF;
            END
            $$;
            """
        )
    )

    enrichment_type = ENUM(
        'semantic', 'performance', 'trend', name='signal_enrichment_type', create_type=False
    )

    # Create signal_enrichments table
    op.create_table(
        'signal_enrichments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('signal_id', UUID(as_uuid=True), sa.ForeignKey('signals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enrichment_type', enrichment_type, nullable=False),
        sa.Column('entities', sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column('sentiment', sa.Float(), nullable=True),
        sa.Column('trend_score', sa.Float(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_signal_enrichments_id', 'signal_enrichments', ['id'])
    op.create_index('ix_signal_enrichments_signal_id', 'signal_enrichments', ['signal_id'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('workspace_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_workspace_id', 'audit_logs', ['workspace_id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])

    # Remove server default from provenance now that existing rows handled
    op.alter_column('signals', 'provenance', server_default=None)


def downgrade() -> None:
    """Drop audit logs, signal enrichments, and provenance column."""
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_workspace_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_id', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_signal_enrichments_signal_id', table_name='signal_enrichments')
    op.drop_index('ix_signal_enrichments_id', table_name='signal_enrichments')
    op.drop_table('signal_enrichments')

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'signal_enrichment_type') THEN
                    DROP TYPE signal_enrichment_type;
                END IF;
            END
            $$;
            """
        )
    )

    op.drop_column('signals', 'provenance')
