from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.review import ReviewStatus


class ReviewCreate(BaseModel):
    title: str
    domain: Optional[str] = None
    research_question: Optional[str] = None


class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    domain: Optional[str] = None
    research_question: Optional[str] = None
    status: Optional[ReviewStatus] = None
    final_review: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    title: str
    domain: Optional[str]
    research_question: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: ReviewStatus
    final_review: Optional[str]
    paper_count: int = 0
    insight_count: int = 0

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
