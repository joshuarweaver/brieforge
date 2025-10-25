"""add_strategic_brief_table

Revision ID: 37180d2a4591
Revises: 6508174fdb87
Create Date: 2025-10-25 00:22:42.515311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision: str = '37180d2a4591'
down_revision: Union[str, None] = '6508174fdb87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create strategic_briefs table."""
    op.create_table(
        'strategic_briefs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='completed'),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('llm_provider', sa.String(), nullable=True),
        sa.Column('llm_model', sa.String(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('content', JSON, nullable=False),
        sa.Column('custom_instructions', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Create indexes
    op.create_index('ix_strategic_briefs_id', 'strategic_briefs', ['id'])
    op.create_index('ix_strategic_briefs_campaign_id', 'strategic_briefs', ['campaign_id'])


def downgrade() -> None:
    """Drop strategic_briefs table."""
    op.drop_index('ix_strategic_briefs_campaign_id', 'strategic_briefs')
    op.drop_index('ix_strategic_briefs_id', 'strategic_briefs')
    op.drop_table('strategic_briefs')
