from fastapi import APIRouter, HTTPException
from app.models.idea import Idea
from app.services.ideas import IdeaService

router = APIRouter()
idea_service = IdeaService()

@router.post("/ideas/", response_model=Idea)
async def create_idea(idea: Idea):
    return await idea_service.create_idea(idea)

@router.get("/ideas/{idea_id}", response_model=Idea)
async def get_idea(idea_id: int):
    idea = await idea_service.get_idea(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.post("/ideas/{idea_id}/vote")
async def vote_on_idea(idea_id: int):
    success = await idea_service.vote_on_idea(idea_id)
    if not success:
        raise HTTPException(status_code=404, detail="Idea not found or already voted")
    return {"message": "Vote recorded successfully"}