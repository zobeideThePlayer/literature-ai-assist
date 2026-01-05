from pydantic import BaseModel
from typing import Optional, List
from app.models.review import ReviewStatus


class AnalysisStartRequest(BaseModel):
    search_query: str
    max_papers: int = 20


class AnalysisStatusResponse(BaseModel):
    review_id: str
    status: ReviewStatus
    papers_found: int
    papers_analyzed: int
    insights_generated: int
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class GenerateReviewRequest(BaseModel):
    include_methodology: bool = True
    include_references: bool = True
