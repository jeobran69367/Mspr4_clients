"""Address model."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AddressType(str, PyEnum):
    """Address type enumeration."""

    LIVRAISON = "livraison"
    FACTURATION = "facturation"
    LIVRAISON_FACTURATION = "livraison_facturation"


class Address(Base):
    """Address database model."""

    __tablename__ = "addresses"

    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)

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
