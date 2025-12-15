from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, CheckConstraint, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Topic(Base):
    __tablename__ = "topics"

    topic_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="topic")
    study_sessions = relationship("StudySession", back_populates="topic")


class Question(Base):
    __tablename__ = "questions"

    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.topic_id"), nullable=True, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(Text, nullable=False)
    option_b: Mapped[str] = mapped_column(Text, nullable=False)
    option_c: Mapped[str] = mapped_column(Text, nullable=False)
    option_d: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", index=True)
    source: Mapped[str] = mapped_column(String(50), default="claude")
    quality_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=4.0)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("correct_answer IN ('a', 'b', 'c', 'd')", name="check_correct_answer"),
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="check_difficulty"),
    )

    # Relationships
    topic: Mapped[Optional["Topic"]] = relationship("Topic", back_populates="questions")
    user_answers = relationship("UserAnswer", back_populates="question", cascade="all, delete-orphan")
    mistake_notes = relationship("MistakeNote", back_populates="question", cascade="all, delete-orphan")
