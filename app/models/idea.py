from sqlalchemy import Column, String, Boolean, Integer, Enum, UUID, ForeignKey, Index, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TEXT
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import expression
from uuid import uuid4
from datetime import datetime
from typing import Optional, List
import re

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(220), unique=True, nullable=False)
    summary = Column(String(500), nullable=False)
    details = Column(TEXT, nullable=False)
    category = Column(Enum('industry', 'technology', 'problem_area', name='category_enum'), nullable=False)
    is_new = Column(Boolean, nullable=False)
    status = Column(Enum('pending', 'approved', 'rejected', name='status_enum'), 
                  default='pending', index=True)
    submitted_by = Column(String(100), nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)
    downvotes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    votes = relationship("Vote", back_populates="idea", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_idea_search', 'title', 'summary', 'details', postgresql_using='gin'),
        CheckConstraint('char_length(title) >= 10', name='title_min_length'),
        CheckConstraint('char_length(summary) BETWEEN 50 AND 500', name='summary_length'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slug = self.generate_slug()

    def generate_slug(self) -> str:
        base = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', base).strip('-')
        return f"{slug}-{uuid4().hex[:6]}"

class Vote(Base):
    __tablename__ = "votes"
    
    idea_id = Column(PG_UUID(as_uuid=True), ForeignKey('ideas.id', ondelete='CASCADE'), primary_key=True)
    voter_hash = Column(String(64), primary_key=True)
    vote_type = Column(Enum('upvote', 'downvote', name='vote_enum'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    idea = relationship("Idea", back_populates="votes")

    __table_args__ = (
        Index('ix_vote_voter', 'voter_hash', postgresql_using='hash'),
    )
    