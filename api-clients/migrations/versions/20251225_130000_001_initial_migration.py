"""Initial migration - create customers, addresses, and user_auth tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-25 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('reference', sa.String(20), nullable=False, unique=True, index=True),
        sa.Column('civilite', sa.String(10), nullable=True),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.Column('prenom', sa.String(100), nullable=False),
        sa.Column('email', sa.String(150), nullable=False, unique=True, index=True),
        sa.Column('telephone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('type_client', sa.Enum('particulier', 'professionnel', 'distributeur', 'admin', name='customertype'), nullable=False, server_default='particulier'),
        sa.Column('statut', sa.Enum('actif', 'inactif', 'suspendu', 'en_attente', name='customerstatus'), nullable=False, server_default='actif'),
        sa.Column('raison_sociale', sa.String(200), nullable=True),
        sa.Column('siret', sa.String(14), nullable=True, unique=True),
        sa.Column('tva_intracommunautaire', sa.String(20), nullable=True),
        sa.Column('nom_contact', sa.String(100), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('email_confirme', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('date_derniere_connexion', sa.DateTime(), nullable=True),
        sa.Column('preferences', sa.Text(), nullable=True),
        sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('date_modification', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
        sa.Column('date_desactivation', sa.DateTime(), nullable=True),
    )
    
    # Create composite indexes
    op.create_index('idx_customer_type_status', 'customers', ['type_client', 'statut'])
    op.create_index('idx_customer_email_status', 'customers', ['email', 'statut'])
    
    # Create addresses table
    op.create_table(
        'addresses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type_adresse', sa.Enum('livraison', 'facturation', 'livraison_facturation', name='addresstype'), nullable=False),
        sa.Column('est_defaut', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('nom_complet', sa.String(200), nullable=True),
        sa.Column('adresse_ligne1', sa.String(255), nullable=False),
        sa.Column('adresse_ligne2', sa.String(255), nullable=True),
        sa.Column('code_postal', sa.String(10), nullable=False),
        sa.Column('ville', sa.String(100), nullable=False),
        sa.Column('region', sa.String(100), nullable=True),
        sa.Column('pays', sa.String(100), nullable=False, server_default='France'),
        sa.Column('telephone', sa.String(20), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('date_modification', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )
    
    # Create composite indexes for addresses
    op.create_index('idx_address_customer_type', 'addresses', ['customer_id', 'type_adresse'])
    op.create_index('idx_address_customer_default', 'addresses', ['customer_id', 'est_defaut'])
    
    # Create user_auth table for refresh tokens
    op.create_table(
        'user_auth',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('refresh_token', sa.String(500), nullable=False, unique=True, index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('date_creation', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Create index for token lookup
    op.create_index('idx_user_auth_customer_active', 'user_auth', ['customer_id', 'is_revoked'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_auth')
    op.drop_table('addresses')
    op.drop_table('customers')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS addresstype')
    op.execute('DROP TYPE IF EXISTS customerstatus')
    op.execute('DROP TYPE IF EXISTS customertype')
