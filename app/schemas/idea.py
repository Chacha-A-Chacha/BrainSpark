# app/schemas/idea.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Union, Dict, Any
from uuid import UUID
from datetime import datetime


class IdeaCreate(BaseModel):
    title: Union[str, Dict[str, Any]]
    summary: Union[str, Dict[str, Any]]
    details: Union[str, Dict[str, Any]]
    category: str
    is_new: bool

    @field_validator('title', 'summary', 'details', mode='before')
    @classmethod
    def extract_string_value(cls, v):
        if isinstance(v, dict):
            return v.get('stringValue', '')

        if isinstance(v, str):
            return v

        return ''

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": {"stringValue": "Innovative Solution"},
                "summary": {"stringValue": "A great approach"},
                "details": {"stringValue": "Detailed explanation"},
                "category": "technology",
                "is_new": True
            }
        }
    )


class IdeaResponse(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    is_new: bool
    submitted_by: str
    upvotes: int
    downvotes: int
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class VoteRequest(BaseModel):
    vote_type: str
