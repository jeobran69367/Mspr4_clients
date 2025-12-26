"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api.v1 import api_router
from app.events.producer import event_producer
from app.events.consumer import event_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    # Only connect to RabbitMQ if it's configured
    if settings.RABBITMQ_HOST:
        try:
            await event_producer.connect()
            # Note: Consumer would be started in a separate background task if needed
        except Exception as e:
            print(f"Warning: Failed to connect to RabbitMQ: {e}")
            print("Application will run without event messaging capabilities")
    else:
        print("RabbitMQ not configured - running without event messaging")
    
    yield
    
    # Shutdown
    try:
        await event_producer.close()
        await event_consumer.close()
    except Exception:
        pass  # Ignore shutdown errors


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
