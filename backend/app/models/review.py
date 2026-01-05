import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ReviewStatus(str, enum.Enum):
    CREATED = "created"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class ReviewSession(Base):
    __tablename__ = "review_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    domain = Column(String(200), nullable=True)
    research_question = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.CREATED)
    final_review = Column(Text, nullable=True)

    papers = relationship("Paper", back_populates="review_session", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="review_session", cascade="all, delete-orphan")
