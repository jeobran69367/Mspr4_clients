"""User authentication model."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class UserAuth(Base):
    """User authentication model for refresh tokens and sessions."""

    __tablename__ = "user_auth"

    # Identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)

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
