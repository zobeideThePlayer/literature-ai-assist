from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from app.database import get_db
from app.models.paper import Paper, PaperSource
from app.models.review import ReviewSession
from app.schemas.paper import PaperResponse, PaperSearchRequest, PaperSearchResponse, PaperSearchResult
from app.services.pubmed import PubMedService
from app.services.semantic_scholar import SemanticScholarService

router = APIRouter(prefix="/api/papers", tags=["papers"])

pubmed_service = PubMedService()
semantic_scholar_service = SemanticScholarService()


@router.post("/search", response_model=PaperSearchResponse)
async def search_papers(request: PaperSearchRequest):
    """Search for papers across configured sources."""
    all_papers: List[PaperSearchResult] = []

    # Search in parallel across sources
    tasks = []
    if PaperSource.PUBMED in request.sources:
        tasks.append(pubmed_service.search(request.query, request.max_results))
    if PaperSource.SEMANTIC_SCHOLAR in request.sources:
        tasks.append(semantic_scholar_service.search(request.query, request.max_results))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            continue  # Skip failed sources
        all_papers.extend(result)

    # Deduplicate by DOI if available
    seen_dois = set()
    seen_titles = set()
    unique_papers = []

    for paper in all_papers:
        if paper.doi:
            if paper.doi not in seen_dois:
                seen_dois.add(paper.doi)
                unique_papers.append(paper)
        else:
            # Fallback to title-based deduplication
            title_lower = paper.title.lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_papers.append(paper)

    return PaperSearchResponse(
        papers=unique_papers[:request.max_results],
        total_found=len(unique_papers),
        query=request.query
    )


@router.post("/{review_id}/add")
async def add_paper_to_review(
    review_id: str,
    paper: PaperSearchResult,
    db: Session = Depends(get_db)
):
    """Add a paper to a review session."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Check if paper already exists in this review
    existing = db.query(Paper).filter(
        Paper.review_session_id == review_id,
        Paper.external_id == paper.external_id,
        Paper.source == paper.source
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Paper already added to this review")

    db_paper = Paper(
        review_session_id=review_id,
        source=paper.source,
        external_id=paper.external_id,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        publication_date=paper.publication_date,
        doi=paper.doi,
        url=paper.url,
        pdf_url=paper.pdf_url
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)

    return PaperResponse(
        id=db_paper.id,
        source=db_paper.source,
        external_id=db_paper.external_id,
        title=db_paper.title,
        authors=db_paper.authors,
        abstract=db_paper.abstract,
        publication_date=db_paper.publication_date,
        doi=db_paper.doi,
        url=db_paper.url,
        pdf_url=db_paper.pdf_url,
        relevance_score=db_paper.relevance_score,
        relevance_explanation=db_paper.relevance_explanation,
        key_findings=db_paper.key_findings or [],
        created_at=db_paper.created_at
    )


@router.get("/{review_id}/list", response_model=List[PaperResponse])
async def list_review_papers(review_id: str, db: Session = Depends(get_db)):
    """List all papers in a review session."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    papers = db.query(Paper).filter(Paper.review_session_id == review_id).order_by(Paper.relevance_score.desc().nullslast()).all()

    return [
        PaperResponse(
            id=paper.id,
            source=paper.source,
            external_id=paper.external_id,
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            publication_date=paper.publication_date,
            doi=paper.doi,
            url=paper.url,
            pdf_url=paper.pdf_url,
            relevance_score=paper.relevance_score,
            relevance_explanation=paper.relevance_explanation,
            key_findings=paper.key_findings or [],
            created_at=paper.created_at
        )
        for paper in papers
    ]


@router.delete("/{review_id}/papers/{paper_id}")
async def remove_paper_from_review(review_id: str, paper_id: str, db: Session = Depends(get_db)):
    """Remove a paper from a review session."""
    paper = db.query(Paper).filter(
        Paper.id == paper_id,
        Paper.review_session_id == review_id
    ).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found in this review")

    db.delete(paper)
    db.commit()
    return {"message": "Paper removed successfully"}
