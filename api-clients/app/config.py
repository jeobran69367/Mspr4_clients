"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "PayeTonKawa - Service Clients"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
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
    
    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
