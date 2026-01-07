# api-clients/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

Base = declarative_base()

# Vérifier si nous sommes en mode test
TESTING = os.getenv("TESTING", "false").lower() == "true"

if TESTING:
    # Mode test: utiliser SQLite synchrone
    print("🔧 Using synchronous SQLite for testing")
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL, echo=settings.DEBUG, connect_args={"check_same_thread": False})
else:
    # Mode production: utiliser PostgreSQL
    print("🚀 Using PostgreSQL for production")
    # Convertir l'URL asynchrone en URL synchrone pour SQLAlchemy standard
    if settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    elif settings.DATABASE_URL.startswith("sqlite+aiosqlite://"):
        DATABASE_URL = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    else:
        DATABASE_URL = settings.DATABASE_URL
    
    engine = create_engine(DATABASE_URL, echo=settings.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()