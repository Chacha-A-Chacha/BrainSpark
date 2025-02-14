from fastapi import APIRouter, HTTPException
from app.models.idea import Idea
from app.services.ideas import IdeaService

router = APIRouter()
idea_service = IdeaService()


@router.post("/approve/{idea_id}")
async def approve_idea(idea_id: int):
    idea = idea_service.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea_service.approve_idea(idea_id)
    return {"message": "Idea approved successfully"}


@router.delete("/reject/{idea_id}")
async def reject_idea(idea_id: int):
    idea = idea_service.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea_service.reject_idea(idea_id)
    return {"message": "Idea rejected successfully"}
