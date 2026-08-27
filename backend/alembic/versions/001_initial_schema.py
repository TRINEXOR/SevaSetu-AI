"""
SevaSetu AI — Initial Database Migration
Author: Rahul Jha | Made in India 🇮🇳
Revision: 001 — Create all tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all SevaSetu AI tables."""

    # users
    op.create_table(
        'users',
        sa.Column('id',            sa.Integer(),      nullable=False, autoincrement=True),
        sa.Column('name',          sa.String(100),    nullable=False),
        sa.Column('email',         sa.String(150),    nullable=False),
        sa.Column('mobile',        sa.String(15),     nullable=False),
        sa.Column('password_hash', sa.String(255),    nullable=False),
        sa.Column('role',          sa.Enum('user','admin'), nullable=False, server_default='user'),
        sa.Column('state',         sa.String(60),     nullable=True),
        sa.Column('language',      sa.String(5),      nullable=False, server_default='en'),
        sa.Column('avatar_url',    sa.String(500),    nullable=True),
        sa.Column('is_active',     sa.Boolean(),      nullable=False, server_default='1'),
        sa.Column('is_verified',   sa.Boolean(),      nullable=False, server_default='0'),
        sa.Column('created_at',    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',    sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email',  name='uq_users_email'),
        sa.UniqueConstraint('mobile', name='uq_users_mobile'),
    )
    op.create_index('idx_users_role',      'users', ['role'])
    op.create_index('idx_users_state',     'users', ['state'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])

    # query_history
    op.create_table(
        'query_history',
        sa.Column('id',            sa.Integer(),  nullable=False, autoincrement=True),
        sa.Column('user_id',       sa.Integer(),  nullable=False),
        sa.Column('question',      sa.Text(),     nullable=False),
        sa.Column('ai_response',   sa.Text(),     nullable=False),
        sa.Column('category',      sa.String(50), nullable=True),
        sa.Column('language',      sa.String(5),  nullable=False, server_default='en'),
        sa.Column('confidence',    sa.Float(),    nullable=False, server_default='0.0'),
        sa.Column('sources',       sa.Text(),     nullable=True),
        sa.Column('is_bookmarked', sa.Boolean(),  nullable=False, server_default='0'),
        sa.Column('created_at',    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_qh_user_id',  'query_history', ['user_id'])
    op.create_index('idx_qh_category', 'query_history', ['category'])
    op.create_index('idx_qh_created',  'query_history', ['created_at'])

    # query_feedback
    op.create_table(
        'query_feedback',
        sa.Column('id',         sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('query_id',   sa.Integer(), nullable=False),
        sa.Column('user_id',    sa.Integer(), nullable=False),
        sa.Column('rating',     sa.Integer(), nullable=False),
        sa.Column('is_helpful', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('comment',    sa.Text(),    nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query_id', 'user_id', name='uq_feedback_query_user'),
        sa.ForeignKeyConstraint(['query_id'], ['query_history.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'],  ['users.id'],         ondelete='CASCADE'),
    )

    # schemes
    op.create_table(
        'schemes',
        sa.Column('id',                   sa.Integer(),     nullable=False, autoincrement=True),
        sa.Column('name',                 sa.String(200),   nullable=False),
        sa.Column('short_name',           sa.String(50),    nullable=True),
        sa.Column('description',          sa.Text(),        nullable=False),
        sa.Column('category',             sa.Enum('agriculture','health','education','housing','women','finance','employment','social','digital'), nullable=False),
        sa.Column('ministry',             sa.String(200),   nullable=True),
        sa.Column('benefits',             sa.Text(),        nullable=True),
        sa.Column('eligibility_criteria', mysql.JSON(),     nullable=True),
        sa.Column('eligibility_text',     sa.Text(),        nullable=True),
        sa.Column('required_documents',   mysql.JSON(),     nullable=True),
        sa.Column('application_url',      sa.String(500),   nullable=True),
        sa.Column('helpline',             sa.String(50),    nullable=True),
        sa.Column('application_steps',    sa.Text(),        nullable=True),
        sa.Column('states_applicable',    mysql.JSON(),     nullable=True),
        sa.Column('max_income',           sa.Float(),       nullable=True),
        sa.Column('min_age',              sa.Integer(),     nullable=True),
        sa.Column('max_age',              sa.Integer(),     nullable=True),
        sa.Column('gender',               sa.String(10),    nullable=True, server_default='all'),
        sa.Column('is_active',            sa.Boolean(),     nullable=False, server_default='1'),
        sa.Column('is_central',           sa.Boolean(),     nullable=False, server_default='1'),
        sa.Column('launch_date',          sa.Date(),        nullable=True),
        sa.Column('created_at',           sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',           sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_schemes_category',  'schemes', ['category'])
    op.create_index('idx_schemes_is_active', 'schemes', ['is_active'])

    # user_schemes
    op.create_table(
        'user_schemes',
        sa.Column('id',                sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id',           sa.Integer(), nullable=False),
        sa.Column('scheme_id',         sa.Integer(), nullable=False),
        sa.Column('eligibility_score', sa.Float(),   nullable=False, server_default='0.0'),
        sa.Column('status',            sa.Enum('eligible','not_eligible','partial','unknown'), server_default='unknown'),
        sa.Column('checked_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('notes',             sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'scheme_id', name='uq_user_scheme'),
        sa.ForeignKeyConstraint(['user_id'],   ['users.id'],   ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scheme_id'], ['schemes.id'], ondelete='CASCADE'),
    )

    # documents
    op.create_table(
        'documents',
        sa.Column('id',                 sa.Integer(),     nullable=False, autoincrement=True),
        sa.Column('user_id',            sa.Integer(),     nullable=False),
        sa.Column('original_name',      sa.String(255),   nullable=False),
        sa.Column('stored_name',        sa.String(255),   nullable=False),
        sa.Column('file_path',          sa.String(500),   nullable=False),
        sa.Column('file_type',          sa.String(10),    nullable=False),
        sa.Column('file_size_kb',       sa.Integer(),     nullable=True),
        sa.Column('service_type',       sa.String(50),    nullable=True),
        sa.Column('doc_type',           sa.String(50),    nullable=True),
        sa.Column('ocr_status',         sa.Enum('pending','processing','completed','failed'), server_default='pending'),
        sa.Column('extracted_text',     sa.Text(),        nullable=True),
        sa.Column('extracted_fields',   mysql.JSON(),     nullable=True),
        sa.Column('verification_score', sa.Float(),       nullable=True),
        sa.Column('is_valid',           sa.Boolean(),     nullable=True),
        sa.Column('missing_fields',     mysql.JSON(),     nullable=True),
        sa.Column('uploaded_at',        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('processed_at',       sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_name', name='uq_stored_name'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_docs_user',       'documents', ['user_id'])
    op.create_index('idx_docs_service',    'documents', ['service_type'])
    op.create_index('idx_docs_ocr_status', 'documents', ['ocr_status'])

    # document_fields
    op.create_table(
        'document_fields',
        sa.Column('id',          sa.Integer(),     nullable=False, autoincrement=True),
        sa.Column('document_id', sa.Integer(),     nullable=False),
        sa.Column('field_name',  sa.String(100),   nullable=False),
        sa.Column('field_value', sa.Text(),         nullable=True),
        sa.Column('is_verified', sa.Boolean(),     nullable=False, server_default='0'),
        sa.Column('confidence',  sa.Float(),       nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_df_document', 'document_fields', ['document_id'])


def downgrade() -> None:
    """Drop all SevaSetu AI tables."""
    op.drop_table('document_fields')
    op.drop_table('documents')
    op.drop_table('user_schemes')
    op.drop_table('schemes')
    op.drop_table('query_feedback')
    op.drop_table('query_history')
    op.drop_table('users')
