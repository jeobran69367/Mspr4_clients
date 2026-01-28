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


# ==================================================
# Sync engine (Alembic / migrations)
# ==================================================
if DATABASE_URL.startswith("postgresql+asyncpg"):
    SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
elif DATABASE_URL.startswith("sqlite+aiosqlite"):
    SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")
else:
    SYNC_DATABASE_URL = DATABASE_URL

engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==================================================
# Async engine (FastAPI runtime)
# ==================================================
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
elif DATABASE_URL.startswith("sqlite://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "sqlite://", "sqlite+aiosqlite://"
    )
elif DATABASE_URL.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
    ASYNC_DATABASE_URL = DATABASE_URL
else:
    raise ValueError(f"Unsupported database URL: {DATABASE_URL}")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ==================================================
# Dependency
# ==================================================
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
