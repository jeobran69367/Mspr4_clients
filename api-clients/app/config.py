"""Application configuration using Pydantic Settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "PayeTonKawa - Service Clients"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # False pour production
    ENVIRONMENT: str = "production"

    # Database
    DATABASE_URL: str = "postgresql://payetonkawa:payetonkawa@localhost:5432/payetonkawa_clients"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "payetonkawa"
    DATABASE_PASSWORD: str = "payetonkawa"
    DATABASE_NAME: str = "payetonkawa_clients"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ===== RABBITMQ FOR RAILWAY PRODUCTION =====
    # Priority order for Railway:
    # 1. RABBITMQ_PRIVATE_URL (Railway internal network)
    # 2. RABBITMQ_URL (Railway public URL)
    # 3. Constructed from parts
    
    RABBITMQ_PRIVATE_URL: Optional[str] = None  # Railway internal URL
    RABBITMQ_URL: Optional[str] = None  # Railway public URL
    
    # Fallback configuration
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    
    # RabbitMQ Exchange and Queue
    RABBITMQ_EXCHANGE: str = "mspr.events"
    RABBITMQ_QUEUE_CLIENTS: str = "clients.queue"
    
    # Service identification (CRITICAL for Railway)
    SERVICE_NAME: str = "clients"
    
    # Auto-enable RabbitMQ if URL is provided
    @property
    def RABBITMQ_ENABLED(self) -> bool:
        """Auto-enable RabbitMQ if any URL is provided"""
        return bool(self.RABBITMQ_PRIVATE_URL or self.RABBITMQ_URL)

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # API
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()