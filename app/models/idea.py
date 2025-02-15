from sqlalchemy import Column, String, Boolean, Integer, Enum, ForeignKey, Index, CheckConstraint, func, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from uuid import uuid4
from datetime import datetime
from typing import Optional, List
import re

from app.db.session import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(220), unique=True, nullable=False)
    summary = Column(String(500), nullable=False)
    details = Column(String(10000), nullable=False)  # Use String instead of TEXT for MySQL
    category = Column(Enum('industry', 'technology', 'problem_area'), nullable=False)
    is_new = Column(Boolean, nullable=False)
    status = Column(Enum('pending', 'approved', 'rejected'),
                    default='pending', index=True)
    submitted_by = Column(String(100), nullable=False)
    upvotes = Column(Integer, default=0, nullable=False)
    downvotes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    votes = relationship("Vote", back_populates="idea", cascade="all, delete-orphan")

    __table_args__ = (
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

    idea_id = Column(String(36), ForeignKey('ideas.id', ondelete='CASCADE'), primary_key=True)
    voter_hash = Column(String(64), primary_key=True)
    vote_type = Column(Enum('upvote', 'downvote'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    idea = relationship("Idea", back_populates="votes")