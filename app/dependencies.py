# app/dependencies.py
from fastapi import Request, Depends
from slowapi import Limiter
from typing import Annotated
from .db.session import get_db
from .services.ideas import IdeaService
from .security import (
    security_service,
    submission_limiter,
    voting_limiter,
    verify_captcha_dependency,
    SanitizedText
)
from .config import settings

def get_idea_service(db: Annotated[AsyncSession, Depends(get_db)]) -> IdeaService:
    """Dependency injection for IdeaService with async support"""
    return IdeaService(db)

def get_voter_identifier(request: Request) -> str:
    """Get secure voter hash using security service"""
    return security_service.get_voter_identifier(request)

def get_submission_limiter() -> Limiter:
    """Dependency for submission rate limiting"""
    return submission_limiter

def get_voting_limiter() -> Limiter:
    """Dependency for voting rate limiting"""
    return voting_limiter

# Typed dependencies for reuse
VoterHashDep = Annotated[str, Depends(get_voter_identifier)]
CaptchaDep = Annotated[None, Depends(verify_captcha_dependency)]
SubmissionLimitDep = Annotated[Limiter, Depends(get_submission_limiter)]
VotingLimitDep = Annotated[Limiter, Depends(get_voting_limiter)]
SanitizedTextDep = Annotated[str, SanitizedText]
