import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class InsightType(str, enum.Enum):
    OBSERVATION = "observation"  # Direct observation from a paper
    CONNECTION = "connection"    # Connection between papers
    THEME = "theme"              # Identified theme across papers
    GAP = "gap"                  # Research gap identified
    CONTRADICTION = "contradiction"  # Contradictory findings
    CONCLUSION = "conclusion"    # Final conclusion/synthesis


class Insight(Base):
    __tablename__ = "insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_session_id = Column(String(36), ForeignKey("review_sessions.id"), nullable=False)
    paper_id = Column(String(36), ForeignKey("papers.id"), nullable=True)  # Nullable for cross-paper insights
    step_number = Column(Integer, nullable=False)
    insight_type = Column(Enum(InsightType), nullable=False)
    content = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)  # Chain-of-thought explanation
    created_at = Column(DateTime, default=datetime.utcnow)

    review_session = relationship("ReviewSession", back_populates="insights")
    paper = relationship("Paper", back_populates="insights")
