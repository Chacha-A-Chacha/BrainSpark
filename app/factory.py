def create_app():
    from fastapi import FastAPI
    from .config import settings
    from .db.session import init_db
    from .routes import core, admin, health

    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

    # Initialize the database
    init_db()

    # Include routers
    app.include_router(core.router)
    app.include_router(admin.router)
    app.include_router(health.router)

    return app