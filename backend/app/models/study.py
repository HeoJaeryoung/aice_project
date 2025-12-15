from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import uuid

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, CheckConstraint, Numeric, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.topic_id"), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    question_count: Mapped[int] = mapped_column(Integer, default=10)
    status: Mapped[str] = mapped_column(String(20), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    questions_attempted: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('active', 'completed', 'abandoned')", name="check_session_status"),
    )

    # Relationships
    user = relationship("User", back_populates="study_sessions")
    topic = relationship("Topic", back_populates="study_sessions")
    user_answers: Mapped[List["UserAnswer"]] = relationship("UserAnswer", back_populates="session", cascade="all, delete-orphan")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    answer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.question_id", ondelete="CASCADE"))
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("study_sessions.session_id"),
        nullable=True,
        index=True
    )
    user_answer: Mapped[str] = mapped_column(String(1), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("user_answer IN ('a', 'b', 'c', 'd')", name="check_user_answer"),
    )

    # Relationships
    user = relationship("User", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")
    session = relationship("StudySession", back_populates="user_answers")


class MistakeNote(Base):
    __tablename__ = "mistake_notes"

    note_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.question_id", ondelete="CASCADE"))
    mistake_count: Mapped[int] = mapped_column(Integer, default=1)
    first_mistake_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_mistake_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    last_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    mastered: Mapped[bool] = mapped_column(Boolean, default=False)
    mastered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question"),
    )

    # Relationships
    user = relationship("User", back_populates="mistake_notes")
    question = relationship("Question", back_populates="mistake_notes")
