"""Add SMTP config and pending invitations tables

Revision ID: add_smtp_invitations
Revises: add_email_templates
Create Date: 2026-01-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_smtp_invitations'
down_revision = 'add_email_templates'
branch_labels = None
depends_on = None


def upgrade():
    # Create smtp_config table
    op.create_table('smtp_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('smtp_server', sa.String(length=255), nullable=False),
        sa.Column('smtp_port', sa.Integer(), nullable=False),
        sa.Column('smtp_username', sa.String(length=255), nullable=False),
        sa.Column('smtp_password', sa.String(length=255), nullable=False),
        sa.Column('smtp_use_tls', sa.Boolean(), nullable=True),
        sa.Column('smtp_use_ssl', sa.Boolean(), nullable=True),
        sa.Column('sender_email', sa.String(length=255), nullable=False),
        sa.Column('sender_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create pending_invitations table
    op.create_table('pending_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('invitation_token', sa.String(length=255), nullable=False),
        sa.Column('supabase_user_id', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['invited_by'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('invitation_token'),
        sa.UniqueConstraint('supabase_user_id')
    )


def downgrade():
    op.drop_table('pending_invitations')
    op.drop_table('smtp_config')
