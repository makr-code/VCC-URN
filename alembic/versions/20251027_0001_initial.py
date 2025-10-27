"""initial schema

Revision ID: 20251027_0001
Revises: 
Create Date: 2025-10-27 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251027_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'manifests',
        sa.Column('urn', sa.String(length=512), primary_key=True, nullable=False),
        sa.Column('nid', sa.String(length=32), nullable=False),
        sa.Column('state', sa.String(length=10), nullable=False),
        sa.Column('domain', sa.String(length=64), nullable=False),
        sa.Column('obj_type', sa.String(length=64), nullable=False),
        sa.Column('local_aktenzeichen', sa.String(length=512), nullable=True),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('version', sa.String(length=64), nullable=True),
        sa.Column('manifest_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_manifests_urn', 'manifests', ['urn'], unique=False)
    op.create_index('ix_manifests_state', 'manifests', ['state'], unique=False)
    op.create_index('ix_manifests_uuid', 'manifests', ['uuid'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_manifests_uuid', table_name='manifests')
    op.drop_index('ix_manifests_state', table_name='manifests')
    op.drop_index('ix_manifests_urn', table_name='manifests')
    op.drop_table('manifests')
