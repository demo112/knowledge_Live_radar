"""add executed_at to approvals

Revision ID: 112233445566
Revises: df696bfff2e7
Create Date: 2026-02-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '112233445566'
down_revision = 'df696bfff2e7'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('approvals', sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('approvals', 'executed_at')
