"""User authentication model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

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


class UserAuth(Base):
    """User authentication model for refresh tokens and sessions."""

    __tablename__ = "user_auth"

    # Identifiers
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)

    # Token information
    refresh_token = Column(String(500), unique=True, nullable=False)
    token_expiry = Column(DateTime, nullable=False)

    # Device/Session information
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Metadata
    date_creation = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_derniere_utilisation = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserAuth(id={self.id}, customer_id={self.customer_id})>"
