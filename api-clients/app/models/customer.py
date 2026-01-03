"""Customer model."""
from sqlalchemy import Column, String, Enum, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from app.models.base import Base


class CustomerType(str, PyEnum):
    """Customer type enumeration."""

    PARTICULIER = "particulier"
    PROFESSIONNEL = "professionnel"
    DISTRIBUTEUR = "distributeur"
    ADMIN = "admin"


class CustomerStatus(str, PyEnum):
    """Customer status enumeration."""

    ACTIF = "actif"
    INACTIF = "inactif"
    SUSPENDU = "suspendu"
    EN_ATTENTE = "en_attente"


class Customer(Base):
    """Customer database model."""

    __tablename__ = "customers"

    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference = Column(String(20), unique=True, nullable=False, index=True)

    # Personal information
    civilite = Column(String(10), nullable=True)  # "M", "Mme", "Mlle"
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    telephone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)

    # Type and status
    type_client = Column(Enum(CustomerType), default=CustomerType.PARTICULIER)
    statut = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIF)

    # Professional information (if type = PROFESSIONNEL or DISTRIBUTEUR)
    raison_sociale = Column(String(200), nullable=True)
    siret = Column(String(14), nullable=True, unique=True)
    tva_intracommunautaire = Column(String(20), nullable=True)
    nom_contact = Column(String(100), nullable=True)

    # Authentication
    hashed_password = Column(String(255), nullable=True)
    email_confirme = Column(Boolean, default=False)
    date_derniere_connexion = Column(DateTime, nullable=True)

    # Preferences
    preferences = Column(Text, nullable=True)  # JSON string

    # Metadata
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_desactivation = Column(DateTime, nullable=True)

    # Relations
    adresses = relationship("Address", back_populates="client", cascade="all, delete-orphan")

    # Composite indexes
    __table_args__ = (
        Index("idx_customer_type_status", "type_client", "statut"),
        Index("idx_customer_email_status", "email", "statut"),
    )

    def __repr__(self):
        return f"<Customer(id={self.id}, reference={self.reference}, email={self.email})>"
