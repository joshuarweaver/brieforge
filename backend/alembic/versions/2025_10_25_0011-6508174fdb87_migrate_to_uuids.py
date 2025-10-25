"""migrate_to_uuids

Revision ID: 6508174fdb87
Revises: e944d0368089
Create Date: 2025-10-25 00:11:10.810206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '6508174fdb87'
down_revision: Union[str, None] = 'e944d0368089'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate workspaces, campaigns, signals, and signal_analyses from integer IDs to UUIDs."""

    # Enable uuid-ossp extension for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # 1. Add new UUID columns to all affected tables
    op.add_column('workspaces', sa.Column('uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('campaigns', sa.Column('uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('signals', sa.Column('uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('signal_analyses', sa.Column('uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('generated_assets', sa.Column('uuid', UUID(as_uuid=True), nullable=True))

    # Add UUID foreign key columns
    op.add_column('users', sa.Column('workspace_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('campaigns', sa.Column('workspace_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('signals', sa.Column('campaign_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('signal_analyses', sa.Column('campaign_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('success_patterns', sa.Column('workspace_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('analyses', sa.Column('campaign_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('generated_assets', sa.Column('campaign_uuid', UUID(as_uuid=True), nullable=True))
    op.add_column('asset_ratings', sa.Column('asset_uuid', UUID(as_uuid=True), nullable=True))

    # 2. Populate UUID columns with generated values
    op.execute('UPDATE workspaces SET uuid = uuid_generate_v4()')
    op.execute('UPDATE campaigns SET uuid = uuid_generate_v4()')
    op.execute('UPDATE signals SET uuid = uuid_generate_v4()')
    op.execute('UPDATE signal_analyses SET uuid = uuid_generate_v4()')
    op.execute('UPDATE generated_assets SET uuid = uuid_generate_v4()')

    # 3. Populate foreign key UUID columns by matching integer IDs
    op.execute('''
        UPDATE users SET workspace_uuid = workspaces.uuid
        FROM workspaces
        WHERE users.workspace_id = workspaces.id
    ''')

    op.execute('''
        UPDATE campaigns SET workspace_uuid = workspaces.uuid
        FROM workspaces
        WHERE campaigns.workspace_id = workspaces.id
    ''')

    op.execute('''
        UPDATE signals SET campaign_uuid = campaigns.uuid
        FROM campaigns
        WHERE signals.campaign_id = campaigns.id
    ''')

    op.execute('''
        UPDATE signal_analyses SET campaign_uuid = campaigns.uuid
        FROM campaigns
        WHERE signal_analyses.campaign_id = campaigns.id
    ''')

    op.execute('''
        UPDATE success_patterns SET workspace_uuid = workspaces.uuid
        FROM workspaces
        WHERE success_patterns.workspace_id = workspaces.id
    ''')

    op.execute('''
        UPDATE analyses SET campaign_uuid = campaigns.uuid
        FROM campaigns
        WHERE analyses.campaign_id = campaigns.id
    ''')

    op.execute('''
        UPDATE generated_assets SET campaign_uuid = campaigns.uuid
        FROM campaigns
        WHERE generated_assets.campaign_id = campaigns.id
    ''')

    op.execute('''
        UPDATE asset_ratings SET asset_uuid = generated_assets.uuid
        FROM generated_assets
        WHERE asset_ratings.asset_id = generated_assets.id
    ''')

    # 4. Drop old foreign key constraints
    op.drop_constraint('users_workspace_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('campaigns_workspace_id_fkey', 'campaigns', type_='foreignkey')
    op.drop_constraint('signals_campaign_id_fkey', 'signals', type_='foreignkey')
    op.drop_constraint('signal_analyses_campaign_id_fkey', 'signal_analyses', type_='foreignkey')
    op.drop_constraint('success_patterns_workspace_id_fkey', 'success_patterns', type_='foreignkey')
    op.drop_constraint('analyses_campaign_id_fkey', 'analyses', type_='foreignkey')
    op.drop_constraint('generated_assets_campaign_id_fkey', 'generated_assets', type_='foreignkey')
    op.drop_constraint('asset_ratings_asset_id_fkey', 'asset_ratings', type_='foreignkey')

    # 5. Drop old integer ID and foreign key columns
    op.drop_column('users', 'workspace_id')
    op.drop_column('campaigns', 'workspace_id')
    op.drop_column('signals', 'campaign_id')
    op.drop_column('signal_analyses', 'campaign_id')
    op.drop_column('success_patterns', 'workspace_id')
    op.drop_column('analyses', 'campaign_id')
    op.drop_column('generated_assets', 'campaign_id')
    op.drop_column('asset_ratings', 'asset_id')

    # 6. Drop old primary keys and rename UUID columns to 'id'
    op.drop_constraint('workspaces_pkey', 'workspaces', type_='primary')
    op.drop_constraint('campaigns_pkey', 'campaigns', type_='primary')
    op.drop_constraint('signals_pkey', 'signals', type_='primary')
    op.drop_constraint('signal_analyses_pkey', 'signal_analyses', type_='primary')
    op.drop_constraint('generated_assets_pkey', 'generated_assets', type_='primary')

    op.drop_column('workspaces', 'id')
    op.drop_column('campaigns', 'id')
    op.drop_column('signals', 'id')
    op.drop_column('signal_analyses', 'id')
    op.drop_column('generated_assets', 'id')

    # Rename uuid columns to id
    op.alter_column('workspaces', 'uuid', new_column_name='id')
    op.alter_column('campaigns', 'uuid', new_column_name='id')
    op.alter_column('signals', 'uuid', new_column_name='id')
    op.alter_column('signal_analyses', 'uuid', new_column_name='id')
    op.alter_column('generated_assets', 'uuid', new_column_name='id')

    # Rename foreign key UUID columns
    op.alter_column('users', 'workspace_uuid', new_column_name='workspace_id')
    op.alter_column('campaigns', 'workspace_uuid', new_column_name='workspace_id')
    op.alter_column('signals', 'campaign_uuid', new_column_name='campaign_id')
    op.alter_column('signal_analyses', 'campaign_uuid', new_column_name='campaign_id')
    op.alter_column('success_patterns', 'workspace_uuid', new_column_name='workspace_id')
    op.alter_column('analyses', 'campaign_uuid', new_column_name='campaign_id')
    op.alter_column('generated_assets', 'campaign_uuid', new_column_name='campaign_id')
    op.alter_column('asset_ratings', 'asset_uuid', new_column_name='asset_id')

    # 7. Make new ID columns NOT NULL and set as primary keys
    op.alter_column('workspaces', 'id', nullable=False)
    op.alter_column('campaigns', 'id', nullable=False)
    op.alter_column('signals', 'id', nullable=False)
    op.alter_column('signal_analyses', 'id', nullable=False)
    op.alter_column('generated_assets', 'id', nullable=False)

    op.create_primary_key('workspaces_pkey', 'workspaces', ['id'])
    op.create_primary_key('campaigns_pkey', 'campaigns', ['id'])
    op.create_primary_key('signals_pkey', 'signals', ['id'])
    op.create_primary_key('signal_analyses_pkey', 'signal_analyses', ['id'])
    op.create_primary_key('generated_assets_pkey', 'generated_assets', ['id'])

    # 8. Make foreign key columns NOT NULL where appropriate and create new foreign key constraints
    op.alter_column('campaigns', 'workspace_id', nullable=False)
    op.alter_column('signals', 'campaign_id', nullable=False)
    op.alter_column('signal_analyses', 'campaign_id', nullable=False)
    op.alter_column('success_patterns', 'workspace_id', nullable=False)
    op.alter_column('analyses', 'campaign_id', nullable=False)
    op.alter_column('generated_assets', 'campaign_id', nullable=False)
    op.alter_column('asset_ratings', 'asset_id', nullable=False)

    op.create_foreign_key('users_workspace_id_fkey', 'users', 'workspaces', ['workspace_id'], ['id'])
    op.create_foreign_key('campaigns_workspace_id_fkey', 'campaigns', 'workspaces', ['workspace_id'], ['id'])
    op.create_foreign_key('signals_campaign_id_fkey', 'signals', 'campaigns', ['campaign_id'], ['id'])
    op.create_foreign_key('signal_analyses_campaign_id_fkey', 'signal_analyses', 'campaigns', ['campaign_id'], ['id'])
    op.create_foreign_key('success_patterns_workspace_id_fkey', 'success_patterns', 'workspaces', ['workspace_id'], ['id'])
    op.create_foreign_key('analyses_campaign_id_fkey', 'analyses', 'campaigns', ['campaign_id'], ['id'])
    op.create_foreign_key('generated_assets_campaign_id_fkey', 'generated_assets', 'campaigns', ['campaign_id'], ['id'])
    op.create_foreign_key('asset_ratings_asset_id_fkey', 'asset_ratings', 'generated_assets', ['asset_id'], ['id'])

    # 9. Create indexes on new ID columns
    op.create_index('ix_workspaces_id', 'workspaces', ['id'])
    op.create_index('ix_campaigns_id', 'campaigns', ['id'])
    op.create_index('ix_signals_id', 'signals', ['id'])
    op.create_index('ix_signal_analyses_id', 'signal_analyses', ['id'])
    op.create_index('ix_generated_assets_id', 'generated_assets', ['id'])


def downgrade() -> None:
    """Downgrade is complex and data-lossy - not recommended for production."""
    # This would require converting UUIDs back to integers, which is not practical
    # and would lose data. Keeping it as a placeholder.
    raise NotImplementedError("Downgrade from UUIDs to integers is not supported")
