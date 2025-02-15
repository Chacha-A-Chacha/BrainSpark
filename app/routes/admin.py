from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.models.idea import Idea
from app.services.ideas import IdeaService
from app.dependencies import get_idea_service

router = APIRouter(tags=["Admin"])


@router.post("/approve/{idea_id}")
async def approve_idea(
        idea_id: UUID,
        service: IdeaService = Depends(get_idea_service)
):
    idea = service.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    service.approve_idea(idea_id)
    return {"message": "Idea approved successfully"}


@router.delete("/reject/{idea_id}")
async def reject_idea(
        idea_id: UUID,
        service: IdeaService = Depends(get_idea_service)
):
    idea = service.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    service.reject_idea(idea_id)
    return {"message": "Idea rejected successfully"}
