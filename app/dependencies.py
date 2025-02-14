from fastapi import Depends
from sqlalchemy.orm import Session
from .db.session import get_db

# Dependency to get the database session
def get_database_session() -> Session:
    db = get_db()
    try:
        yield db
    finally:
        db.close()