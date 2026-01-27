"""add_token_template_fields

Revision ID: 67c8e591fada
Revises: cc6c7b01528f
Create Date: 2026-01-26 11:01:16.448633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67c8e591fada'
down_revision = 'cc6c7b01528f'
branch_labels = None
depends_on = None


def upgrade():
    # Add token template fields to events table
    op.add_column('events', sa.Column('token_template_html', sa.Text(), nullable=True))
    op.add_column('events', sa.Column('token_template_css', sa.Text(), nullable=True))


def downgrade():
    # Remove token template fields
    op.drop_column('events', 'token_template_css')
    op.drop_column('events', 'token_template_html')
