from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
from app.database import get_db
from app.models.review import ReviewSession, ReviewStatus
from app.models.paper import Paper
from app.models.insight import Insight, InsightType
from app.schemas.analysis import AnalysisStartRequest, AnalysisStatusResponse, GenerateReviewRequest
from app.schemas.insight import InsightResponse
from app.services.pubmed import PubMedService
from app.services.semantic_scholar import SemanticScholarService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

pubmed_service = PubMedService()
semantic_scholar_service = SemanticScholarService()
llm_service = LLMService()


async def run_analysis_pipeline(review_id: str, search_query: str, max_papers: int, db: Session):
    """Run the full analysis pipeline in the background."""
    try:
        review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
        if not review:
            return

        # Step 1: Search for papers
        review.status = ReviewStatus.SEARCHING
        db.commit()

        # Search both sources
        pubmed_papers = await pubmed_service.search(search_query, max_papers // 2)
        semantic_papers = await semantic_scholar_service.search(search_query, max_papers // 2)
        all_papers = pubmed_papers + semantic_papers

        # Deduplicate
        seen_dois = set()
        unique_papers = []
        for paper in all_papers:
            if paper.doi and paper.doi in seen_dois:
                continue
            if paper.doi:
                seen_dois.add(paper.doi)
            unique_papers.append(paper)

        # Add papers to database
        for paper_data in unique_papers[:max_papers]:
            db_paper = Paper(
                review_session_id=review_id,
                source=paper_data.source,
                external_id=paper_data.external_id,
                title=paper_data.title,
                authors=paper_data.authors,
                abstract=paper_data.abstract,
                publication_date=paper_data.publication_date,
                doi=paper_data.doi,
                url=paper_data.url,
                pdf_url=paper_data.pdf_url
            )
            db.add(db_paper)
        db.commit()

        # Step 2: Analyze each paper
        review.status = ReviewStatus.ANALYZING
        db.commit()

        step_number = 1
        papers = db.query(Paper).filter(Paper.review_session_id == review_id).all()

        for paper in papers:
            if not paper.abstract:
                continue

            # Evaluate relevance
            relevance_result = await llm_service.evaluate_relevance(
                title=paper.title,
                abstract=paper.abstract,
                research_question=review.research_question or review.title,
                domain=review.domain or ""
            )

            paper.relevance_score = relevance_result.get("relevance_score", 0.5)
            paper.relevance_explanation = relevance_result.get("explanation", "")

            # Create insight for relevance assessment
            insight = Insight(
                review_session_id=review_id,
                paper_id=paper.id,
                step_number=step_number,
                insight_type=InsightType.OBSERVATION,
                content=f"Relevance: {paper.relevance_score:.2f} - {relevance_result.get('explanation', '')}",
                reasoning=f"Evaluated '{paper.title}' against research question. Key aspects: {', '.join(relevance_result.get('key_aspects', []))}"
            )
            db.add(insight)
            step_number += 1

            # Extract findings for relevant papers
            if paper.relevance_score >= 0.5:
                findings_result = await llm_service.extract_findings(
                    title=paper.title,
                    abstract=paper.abstract,
                    research_question=review.research_question or review.title,
                    domain=review.domain or ""
                )

                paper.key_findings = [f.get("finding", "") for f in findings_result.get("key_findings", [])]

                # Create insight for each finding
                for finding in findings_result.get("key_findings", []):
                    insight = Insight(
                        review_session_id=review_id,
                        paper_id=paper.id,
                        step_number=step_number,
                        insight_type=InsightType.OBSERVATION,
                        content=finding.get("finding", ""),
                        reasoning=f"Evidence: {finding.get('evidence', '')}. Limitations: {finding.get('limitations', '')}"
                    )
                    db.add(insight)
                    step_number += 1

            db.commit()

        # Step 3: Cross-paper analysis
        relevant_papers = db.query(Paper).filter(
            Paper.review_session_id == review_id,
            Paper.relevance_score >= 0.5
        ).all()

        if relevant_papers:
            papers_summary = "\n\n".join([
                f"Title: {p.title}\nFindings: {', '.join(p.key_findings or [])}"
                for p in relevant_papers
            ])

            analysis_result = await llm_service.analyze_papers(
                papers_summary=papers_summary,
                research_question=review.research_question or review.title,
                domain=review.domain or ""
            )

            # Create insights for themes
            for theme in analysis_result.get("themes", []):
                insight = Insight(
                    review_session_id=review_id,
                    step_number=step_number,
                    insight_type=InsightType.THEME,
                    content=theme.get("theme", ""),
                    reasoning=theme.get("reasoning", "")
                )
                db.add(insight)
                step_number += 1

            # Create insights for gaps
            for gap in analysis_result.get("gaps", []):
                insight = Insight(
                    review_session_id=review_id,
                    step_number=step_number,
                    insight_type=InsightType.GAP,
                    content=gap.get("gap", ""),
                    reasoning=gap.get("reasoning", "")
                )
                db.add(insight)
                step_number += 1

            # Create insights for contradictions
            for contradiction in analysis_result.get("contradictions", []):
                insight = Insight(
                    review_session_id=review_id,
                    step_number=step_number,
                    insight_type=InsightType.CONTRADICTION,
                    content=contradiction.get("topic", ""),
                    reasoning=f"Positions: {contradiction.get('positions', [])}. {contradiction.get('reasoning', '')}"
                )
                db.add(insight)
                step_number += 1

            db.commit()

        review.status = ReviewStatus.COMPLETED
        db.commit()

    except Exception as e:
        review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
        if review:
            review.status = ReviewStatus.ERROR
            db.commit()
        raise e


@router.post("/{review_id}/start", response_model=AnalysisStatusResponse)
async def start_analysis(
    review_id: str,
    request: AnalysisStartRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start the analysis pipeline for a review."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.status not in [ReviewStatus.CREATED, ReviewStatus.ERROR, ReviewStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Analysis already in progress")

    # Start background analysis
    background_tasks.add_task(run_analysis_pipeline, review_id, request.search_query, request.max_papers, db)

    review.status = ReviewStatus.SEARCHING
    db.commit()

    return AnalysisStatusResponse(
        review_id=review.id,
        status=review.status,
        papers_found=0,
        papers_analyzed=0,
        insights_generated=0,
        current_step="Searching for papers..."
    )


@router.get("/{review_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(review_id: str, db: Session = Depends(get_db)):
    """Get the current status of an analysis."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    papers_count = db.query(Paper).filter(Paper.review_session_id == review_id).count()
    analyzed_count = db.query(Paper).filter(
        Paper.review_session_id == review_id,
        Paper.relevance_score.isnot(None)
    ).count()
    insights_count = db.query(Insight).filter(Insight.review_session_id == review_id).count()

    current_step = {
        ReviewStatus.CREATED: "Not started",
        ReviewStatus.SEARCHING: "Searching for papers...",
        ReviewStatus.ANALYZING: f"Analyzing papers ({analyzed_count}/{papers_count})...",
        ReviewStatus.GENERATING: "Generating literature review...",
        ReviewStatus.COMPLETED: "Analysis complete",
        ReviewStatus.ERROR: "Error occurred"
    }.get(review.status, "Unknown")

    return AnalysisStatusResponse(
        review_id=review.id,
        status=review.status,
        papers_found=papers_count,
        papers_analyzed=analyzed_count,
        insights_generated=insights_count,
        current_step=current_step
    )


@router.get("/{review_id}/insights", response_model=List[InsightResponse])
async def get_insights(review_id: str, db: Session = Depends(get_db)):
    """Get all insights (chain of thought) for a review."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    insights = db.query(Insight).filter(
        Insight.review_session_id == review_id
    ).order_by(Insight.step_number).all()

    return [
        InsightResponse(
            id=insight.id,
            review_session_id=insight.review_session_id,
            paper_id=insight.paper_id,
            step_number=insight.step_number,
            insight_type=insight.insight_type,
            content=insight.content,
            reasoning=insight.reasoning,
            created_at=insight.created_at
        )
        for insight in insights
    ]


@router.post("/{review_id}/generate-review")
async def generate_review(
    review_id: str,
    request: GenerateReviewRequest,
    db: Session = Depends(get_db)
):
    """Generate the final literature review."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Get papers and insights
    papers = db.query(Paper).filter(
        Paper.review_session_id == review_id,
        Paper.relevance_score >= 0.5
    ).all()

    insights = db.query(Insight).filter(Insight.review_session_id == review_id).all()

    # Prepare summaries
    papers_summary = "\n\n".join([
        f"- {p.title} ({p.publication_date or 'n.d.'}): {', '.join(p.key_findings or ['No specific findings extracted'])}"
        for p in papers
    ])

    themes = "\n".join([
        f"- {i.content}" for i in insights if i.insight_type == InsightType.THEME
    ])

    gaps = "\n".join([
        f"- {i.content}" for i in insights if i.insight_type == InsightType.GAP
    ])

    consensus = "\n".join([
        f"- {i.content}" for i in insights
        if i.insight_type == InsightType.OBSERVATION and i.paper_id is None
    ])

    contradictions = "\n".join([
        f"- {i.content}" for i in insights if i.insight_type == InsightType.CONTRADICTION
    ])

    # Generate the review
    review.status = ReviewStatus.GENERATING
    db.commit()

    try:
        generated_review = await llm_service.generate_review(
            research_question=review.research_question or review.title,
            domain=review.domain or "",
            papers_summary=papers_summary,
            themes=themes or "No specific themes identified",
            gaps=gaps or "No specific gaps identified",
            consensus=consensus or "No consensus points identified",
            contradictions=contradictions or "No contradictions identified"
        )

        review.final_review = generated_review
        review.status = ReviewStatus.COMPLETED
        db.commit()

        # Add final insight
        insight = Insight(
            review_session_id=review_id,
            step_number=db.query(Insight).filter(Insight.review_session_id == review_id).count() + 1,
            insight_type=InsightType.CONCLUSION,
            content="Literature review generated successfully",
            reasoning=f"Synthesized {len(papers)} papers into a comprehensive review covering {len([i for i in insights if i.insight_type == InsightType.THEME])} themes."
        )
        db.add(insight)
        db.commit()

        return {"review": generated_review}

    except Exception as e:
        review.status = ReviewStatus.ERROR
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}/generate-review-stream")
async def generate_review_stream(review_id: str, db: Session = Depends(get_db)):
    """Generate the literature review with streaming output."""
    review = db.query(ReviewSession).filter(ReviewSession.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    papers = db.query(Paper).filter(
        Paper.review_session_id == review_id,
        Paper.relevance_score >= 0.5
    ).all()

    insights = db.query(Insight).filter(Insight.review_session_id == review_id).all()

    papers_summary = "\n\n".join([
        f"- {p.title} ({p.publication_date or 'n.d.'}): {', '.join(p.key_findings or ['No specific findings'])}"
        for p in papers
    ])

    themes = "\n".join([f"- {i.content}" for i in insights if i.insight_type == InsightType.THEME])
    gaps = "\n".join([f"- {i.content}" for i in insights if i.insight_type == InsightType.GAP])
    consensus = ""
    contradictions = "\n".join([f"- {i.content}" for i in insights if i.insight_type == InsightType.CONTRADICTION])

    async def stream_generator():
        full_review = ""
        async for chunk in llm_service.generate_review_stream(
            research_question=review.research_question or review.title,
            domain=review.domain or "",
            papers_summary=papers_summary,
            themes=themes or "No specific themes identified",
            gaps=gaps or "No specific gaps identified",
            consensus=consensus or "No consensus points identified",
            contradictions=contradictions or "No contradictions identified"
        ):
            full_review += chunk
            yield chunk

        # Save the final review
        review.final_review = full_review
        review.status = ReviewStatus.COMPLETED
        db.commit()

    return StreamingResponse(stream_generator(), media_type="text/plain")
