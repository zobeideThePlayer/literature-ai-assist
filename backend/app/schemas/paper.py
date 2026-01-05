from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.paper import PaperSource


class PaperSearchRequest(BaseModel):
    query: str
    max_results: int = 20
    sources: List[PaperSource] = [PaperSource.PUBMED, PaperSource.SEMANTIC_SCHOLAR]


class PaperResponse(BaseModel):
    id: str
    source: PaperSource
    external_id: str
    title: str
    authors: List[str]
    abstract: Optional[str]
    publication_date: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    pdf_url: Optional[str]
    relevance_score: Optional[float]
    relevance_explanation: Optional[str]
    key_findings: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaperSearchResult(BaseModel):
    source: PaperSource
    external_id: str
    title: str
    authors: List[str]
    abstract: Optional[str]
    publication_date: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    pdf_url: Optional[str]


class PaperSearchResponse(BaseModel):
    papers: List[PaperSearchResult]
    total_found: int
    query: str
