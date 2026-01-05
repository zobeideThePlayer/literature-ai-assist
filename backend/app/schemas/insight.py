from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.insight import InsightType


class InsightCreate(BaseModel):
    paper_id: Optional[str] = None
    insight_type: InsightType
    content: str
    reasoning: Optional[str] = None


class InsightResponse(BaseModel):
    id: str
    review_session_id: str
    paper_id: Optional[str]
    step_number: int
    insight_type: InsightType
    content: str
    reasoning: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InsightListResponse(BaseModel):
    insights: List[InsightResponse]
    total: int
