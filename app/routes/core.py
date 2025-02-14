# app/routes/core.py
from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
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
        orm_mode = True


class VoteRequest(BaseModel):
    vote_type: str


# --- Routes ---
@router.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(CaptchaDep)]
)
@SubmissionLimitDep.limit(settings.SUBMISSION_RATE_LIMIT)
async def submit_idea(
        request: Request,
        idea_data: IdeaCreate,
        service: IdeaService = Depends(get_idea_service),
        voter_hash: VoterHashDep
):
    """Submit a new idea (CAPTCHA protected)"""
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
    "/ideas/{idea_id}/vote",
    dependencies=[Depends(VotingLimitDep.limit(settings.VOTING_RATE_LIMIT))]
)
async def vote_idea(
        idea_id: UUID,
        vote_data: VoteRequest,
        service: IdeaService = Depends(get_idea_service),
        voter_hash: VoterHashDep
):
    """Vote on an approved idea"""
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
