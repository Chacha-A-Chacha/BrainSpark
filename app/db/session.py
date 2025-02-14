from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Settings

Base = declarative_base()

# Configure database engine
engine = create_async_engine(
    Settings.DATABASE_URL,
    pool_size=Settings.DB_POOL_SIZE,
    max_overflow=Settings.DB_MAX_OVERFLOW,
    echo=Settings.DEBUG  # Log SQL in development
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def create_db_tables():
    """Initialize database schema"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency for FastAPI route handlers"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
