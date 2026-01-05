from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.review import ReviewSession, ReviewStatus
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate, ReviewListResponse

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new literature review session."""
    db_review = ReviewSession(
        title=review.title,
        domain=review.domain,
        research_question=review.research_question
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return ReviewResponse(
        id=db_review.id,
        title=db_review.title,
        domain=db_review.domain,
        research_question=db_review.research_question,
        created_at=db_review.created_at,
        updated_at=db_review.updated_at,
        status=db_review.status,
        final_review=db_review.final_review,
        paper_count=0,
        insight_count=0
    )


@router.get("", response_model=ReviewListResponse)
async def list_reviews(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all review sessions."""
    reviews = db.query(ReviewSession).order_by(ReviewSession.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(ReviewSession).count()

    response_reviews = []
    for review in reviews:
        response_reviews.append(ReviewResponse(
            id=review.id,
            title=review.title,
            domain=review.domain,
            research_question=review.research_question,
            created_at=review.created_at,
            updated_at=review.updated_at,
            status=review.status,
            final_review=review.final_review,
            paper_count=len(review.papers),
            insight_count=len(review.insights)
        ))

    return ReviewListResponse(reviews=response_reviews, total=total)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, db: Session = Depends(get_db)):
    """Get a specific review session."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return ReviewResponse(
        id=review.id,
        title=review.title,
        domain=review.domain,
        research_question=review.research_question,
        created_at=review.created_at,
        updated_at=review.updated_at,
        status=review.status,
        final_review=review.final_review,
        paper_count=len(review.papers),
        insight_count=len(review.insights)
    )


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: str, update: ReviewUpdate, db: Session = Depends(get_db)):
    """Update a review session."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        title=review.title,
        domain=review.domain,
        research_question=review.research_question,
        created_at=review.created_at,
        updated_at=review.updated_at,
        status=review.status,
        final_review=review.final_review,
        paper_count=len(review.papers),
        insight_count=len(review.insights)
    )


@router.delete("/{review_id}")
async def delete_review(review_id: str, db: Session = Depends(get_db)):
    """Delete a review session."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}
