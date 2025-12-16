from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.question import TopicResponse, QuestionWithAnswerResponse


# Session request schemas
class SessionCreateRequest(BaseModel):
    topic_id: int
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_count: int = Field(default=10, ge=1, le=20)


class SessionEndRequest(BaseModel):
    pass


# Session response schemas
class SessionQuestionResponse(BaseModel):
    question_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str

    class Config:
        from_attributes = True


class SessionCreateResponse(BaseModel):
    session_id: UUID
    topic: TopicResponse
    difficulty: str
    question_count: int
    questions: List[SessionQuestionResponse]
    started_at: datetime


class SessionResponse(BaseModel):
    session_id: UUID
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    difficulty: Optional[str] = None
    question_count: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    questions_attempted: int
    correct_answers: int
    accuracy_rate: Optional[Decimal] = None

    class Config:
        from_attributes = True


class SessionResultResponse(BaseModel):
    session_id: UUID
    status: str
    questions_attempted: int
    correct_answers: int
    accuracy_rate: Optional[Decimal] = None
    duration_seconds: Optional[int] = None
    ended_at: datetime


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    count: int


# Mistake note schemas
class MistakeNoteResponse(BaseModel):
    note_id: int
    question: QuestionWithAnswerResponse
    mistake_count: int
    first_mistake_at: datetime
    last_mistake_at: datetime
    review_count: int
    last_review_at: Optional[datetime] = None
    mastered: bool

    class Config:
        from_attributes = True


class MistakeListResponse(BaseModel):
    mistakes: List[MistakeNoteResponse]
    count: int


# History schemas
class StudyHistoryResponse(BaseModel):
    sessions: List[SessionResponse]
    total_sessions: int
    total_questions: int
    total_correct: int
    overall_accuracy: Optional[Decimal] = None
