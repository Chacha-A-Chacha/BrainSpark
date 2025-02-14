from sqlalchemy import case, update
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Tuple

class IdeaService:
    def __init__(self, db: Session):
        self.db = db

    def submit_idea(self, idea_data: dict, submitted_by: str) -> Idea:
        try:
            idea = Idea(**idea_data, submitted_by=submitted_by)
            self.db.add(idea)
            self.db.commit()
            self.db.refresh(idea)
            return idea
        except IntegrityError as e:
            self.db.rollback()
            if "slug" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idea with similar title already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid idea data"
            )

    def handle_vote(self, idea_id: UUID, voter_hash: str, vote_type: str) -> Tuple[int, int]:
        # Check if idea exists and is approved
        idea = self.db.query(Idea).filter(
            Idea.id == idea_id,
            Idea.status == 'approved'
        ).first()

        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Idea not found or not approved"
            )

        # Use atomic update to prevent race conditions
        update_values = {
            "upvotes": case(
                (Vote.vote_type == 'upvote', Idea.upvotes - 1),
                else_=Idea.upvotes + (vote_type == 'upvote')
            ),
            "downvotes": case(
                (Vote.vote_type == 'downvote', Idea.downvotes - 1),
                else_=Idea.downvotes + (vote_type == 'downvote')
            )
        }

        # Check existing vote using CTE
        existing_vote = self.db.query(Vote).filter(
            Vote.idea_id == idea_id,
            Vote.voter_hash == voter_hash
        ).cte("existing_vote")

        # Perform atomic update
        stmt = (
            update(Idea)
            .where(Idea.id == idea_id)
            .values(**update_values)
            .returning(Idea.upvotes, Idea.downvotes)
        )

        if existing_vote is not None:
            # Update existing vote
            self.db.query(Vote).filter(
                Vote.idea_id == idea_id,
                Vote.voter_hash == voter_hash
            ).update({"vote_type": vote_type})
        else:
            # Create new vote
            self.db.add(Vote(
                idea_id=idea_id,
                voter_hash=voter_hash,
                vote_type=vote_type
            ))

        try:
            result = self.db.execute(stmt).fetchone()
            self.db.commit()
            return (result.upvotes, result.downvotes)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vote processing failed"
            )

    def get_approved_ideas(
        self,
        category: Optional[str] = None,
        sort: str = 'recent',
        page: int = 1,
        per_page: int = 20
    ) -> List[Idea]:
        query = self.db.query(Idea).filter(Idea.status == 'approved')

        if category:
            query = query.filter(Idea.category == category)

        if sort == 'popular':
            query = query.order_by(Idea.upvotes.desc())
        elif sort == 'controversial':
            query = query.order_by((Idea.upvotes - Idea.downvotes).asc())
        else:
            query = query.order_by(Idea.created_at.desc())

        return query.offset((page - 1) * per_page).limit(per_page).all()

    def update_idea_status(self, idea_id: UUID, status: str) -> Idea:
        idea = self.db.query(Idea).get(idea_id)
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        
        if status not in ['approved', 'rejected']:
            raise HTTPException(status_code=400, detail="Invalid status")

        idea.status = status
        self.db.commit()
        return idea
    