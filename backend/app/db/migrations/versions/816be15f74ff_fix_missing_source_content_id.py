"""fix_missing_source_content_id

Revision ID: 816be15f74ff
Revises: 1f0b07462199
Create Date: 2026-02-13 11:47:48.824415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '816be15f74ff'
down_revision = '1f0b07462199'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('approvals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source_content_id', sa.CHAR(32), nullable=True))
        batch_op.add_column(sa.Column('generated_by', sa.String(length=50), server_default='user', nullable=False))
        batch_op.add_column(sa.Column('reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('confidence_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('original_data', sa.JSON(), nullable=True))
        
        batch_op.create_foreign_key('fk_approvals_source_content_id_content_items', 'content_items', ['source_content_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('approvals', schema=None) as batch_op:
        batch_op.drop_constraint('fk_approvals_source_content_id_content_items', type_='foreignkey')
        batch_op.drop_column('original_data')
        batch_op.drop_column('confidence_score')
        batch_op.drop_column('reason')
        batch_op.drop_column('generated_by')
        batch_op.drop_column('source_content_id')
