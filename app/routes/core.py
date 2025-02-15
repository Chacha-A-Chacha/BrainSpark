# app/routes/core.py
from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from slowapi import Limiter

from app.dependencies import (
    VoterHashDep,
    CaptchaDep,
    SubmissionLimitDep,
    VotingLimitDep,
    SanitizedTextDep,
    get_idea_service
)
from app.services.ideas import IdeaService
from app.models import Idea
from app.config import settings
from app.utils.names import generate_animal_name

import os

router = APIRouter(tags=["Ideas"])


# --- Schemas ---
class IdeaCreate(BaseModel):
    title: SanitizedTextDep
    summary: SanitizedTextDep
    details: SanitizedTextDep
    category: str
    is_new: bool


class IdeaResponse(BaseModel):
    id: UUID
    title: str
    summary: str
    category: str
    is_new: bool
    submitted_by: str
    upvotes: int
    downvotes: int
    created_at: str

    class Config:
        from_attributes = True  # Updated from orm_mode


class VoteRequest(BaseModel):
    vote_type: str


# --- Routes ---
# Modify the decorator to handle migrations
def submission_rate_limit_decorator(func):
    # If running in migration context, skip rate limiting
    if os.environ.get('RUNNING_MIGRATION'):
        return func

    # Otherwise, apply the rate limit
    from app.dependencies import submission_limiter
    return submission_limiter.limit(settings.SUBMISSION_RATE_LIMIT)(func)


# Similarly for voting
def voting_rate_limit_decorator(func):
    # If running in migration context, skip rate limiting
    if os.environ.get('RUNNING_MIGRATION'):
        return func

    # Otherwise, apply the rate limit
    from app.dependencies import voting_limiter
    return voting_limiter.limit(settings.VOTING_RATE_LIMIT)(func)


@router.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(CaptchaDep)]
)
@submission_rate_limit_decorator
async def submit_idea(
        request: Request,
        idea_data: IdeaCreate,
        voter_hash: VoterHashDep,
        service: IdeaService = Depends(get_idea_service)
):
    """Submit a new idea (CAPTCHA protected)"""
    # Rate limiting is now handled by the decorator

    try:
        idea = service.submit_idea(
            idea_data.dict(),
            submitted_by=generate_animal_name()
        )
        return idea
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )


@router.post(
    "/ideas/{idea_id}/vote"
)
@voting_rate_limit_decorator
async def vote_idea(
        idea_id: UUID,
        vote_data: VoteRequest,
        request: Request,
        voter_hash: VoterHashDep,
        service: IdeaService = Depends(get_idea_service)
):
    """Vote on an approved idea"""
    # Rate limiting is now handled by the decorator

    try:
        upvotes, downvotes = service.handle_vote(
            idea_id,
            voter_hash,
            vote_data.vote_type
        )
        return {
            "idea_id": str(idea_id),
            "upvotes": upvotes,
            "downvotes": downvotes
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Voting failed"}
        )


@router.get("/ideas", response_model=List[IdeaResponse])
async def get_ideas(
        category: Optional[str] = None,
        sort: str = "recent",
        page: int = 1,
        per_page: int = 20,
        service: IdeaService = Depends(get_idea_service)
):
    """Get approved ideas with sorting and filtering"""
    try:
        ideas = service.get_approved_ideas(
            category=category,
            sort=sort,
            page=page,
            per_page=per_page
        )
        return ideas
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid request parameters"}
        )
