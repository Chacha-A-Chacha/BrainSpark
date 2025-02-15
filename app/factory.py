# app/factory.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from app.config import settings
from app.db.session import init_db as create_db_tables, get_db
from app.routes import core, admin, health
import logging

logger = logging.getLogger(__name__)


def setup_basic_logging():
    """Minimal logging setup for MVP"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for database initialization"""
    logger.info("Starting application lifecycle")
    await create_db_tables()
    yield
    logger.info("Closing application")


def create_app() -> FastAPI:
    """Core factory function for MVP"""
    setup_basic_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include essential routes
    app.include_router(health.router)
    app.include_router(core.router, prefix="/api")
    app.include_router(admin.router, prefix="/api/admin")

    # Add metrics if enabled
    if settings.ENABLE_PROMETHEUS:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    return app


app = create_app()
