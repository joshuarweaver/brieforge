"""add_campaign_blueprints_table

Revision ID: c2d3e4f5a6b7
Revises: b7c8d9e0f1a2
Create Date: 2025-10-25 21:56:56.766346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'campaign_blueprints',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('blueprint', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_campaign_blueprints_id', 'campaign_blueprints', ['id'])
    op.create_index('ix_campaign_blueprints_campaign_id', 'campaign_blueprints', ['campaign_id'])


def downgrade() -> None:
    op.drop_index('ix_campaign_blueprints_campaign_id', table_name='campaign_blueprints')
    op.drop_index('ix_campaign_blueprints_id', table_name='campaign_blueprints')
    op.drop_table('campaign_blueprints')

