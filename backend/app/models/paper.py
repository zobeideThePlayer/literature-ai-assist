import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PaperSource(str, enum.Enum):
    PUBMED = "pubmed"
    SEMANTIC_SCHOLAR = "semantic_scholar"


class Paper(Base):
    __tablename__ = "papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_session_id = Column(String(36), ForeignKey("review_sessions.id"), nullable=False)
    source = Column(Enum(PaperSource), nullable=False)
    external_id = Column(String(100), nullable=False)
    title = Column(String(1000), nullable=False)
    authors = Column(JSON, default=list)
    abstract = Column(Text, nullable=True)
    publication_date = Column(String(50), nullable=True)
    doi = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    full_text = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    relevance_explanation = Column(Text, nullable=True)
    key_findings = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    review_session = relationship("ReviewSession", back_populates="papers")
    insights = relationship("Insight", back_populates="paper")
