# app/__init__.py
from .factory import create_app

app = create_app()

__all__ = ["app"]
