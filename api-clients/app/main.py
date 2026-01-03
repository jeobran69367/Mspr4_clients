"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import subprocess

from app.config import settings
from app.api.v1 import api_router
from app.events.producer import event_producer
from app.events.consumer import event_consumer

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations."""
    try:
        logger.info("Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Database migrations applied successfully")
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""

    # 1️⃣ Run database migrations FIRST
    run_migrations()

    # 2️⃣ Connect to RabbitMQ (non bloquant)
    if settings.RABBITMQ_HOST:
        try:
            await event_producer.connect()
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.warning(f"RabbitMQ unavailable: {e}")
    else:
        logger.info("RabbitMQ not configured")

    yield

    # Shutdown
    try:
        await event_producer.close()
        await event_consumer.close()
    except Exception:
        pass


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
