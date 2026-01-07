"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.config import settings

DATABASE_URL = settings.DATABASE_URL

# -----------------------------
# Sync engine (migrations)
# -----------------------------
engine = create_engine(
    DATABASE_URL.replace("+asyncpg", ""),
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# -----------------------------
# Async engine (application)
# -----------------------------
if DATABASE_URL.startswith("postgresql"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
elif DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "sqlite://", "sqlite+aiosqlite://"
    )
else:
    raise ValueError(f"Unsupported database driver in {DATABASE_URL}")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# -----------------------------
# Dependency
# -----------------------------
async def get_db():
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        yield session
