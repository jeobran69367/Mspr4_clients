"""Address model."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class UUID(TypeDecorator):
    """Platform-independent UUID type.
    
    Uses PostgreSQL's UUID type on PostgreSQL, otherwise uses
    CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


class AddressType(str, PyEnum):
    """Address type enumeration."""

    LIVRAISON = "livraison"
    FACTURATION = "facturation"
    LIVRAISON_FACTURATION = "livraison_facturation"


class Address(Base):
    """Address database model."""

    __tablename__ = "addresses"

    # Identifiers
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)

    # Address type
    type_adresse = Column(Enum(AddressType), nullable=False)
    est_defaut = Column(Boolean, default=False)

    # Address details
    libelle = Column(String(100), nullable=True)  # "Domicile", "Bureau", etc.
    destinataire = Column(String(100), nullable=True)
    adresse_ligne1 = Column(String(255), nullable=False)
    adresse_ligne2 = Column(String(255), nullable=True)
    code_postal = Column(String(10), nullable=False)
    ville = Column(String(100), nullable=False)
    pays = Column(String(100), default="France", nullable=False)

    # Additional information
    instructions_livraison = Column(String(500), nullable=True)
    telephone = Column(String(20), nullable=True)

    # Metadata
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    client = relationship("Customer", back_populates="adresses")

    def __repr__(self):
        return f"<Address(id={self.id}, type={self.type_adresse}, ville={self.ville})>"
