from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field


# Topic schemas
class TopicResponse(BaseModel):
    topic_id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    display_order: int

    class Config:
        from_attributes = True


class TopicListResponse(BaseModel):
    topics: List[TopicResponse]
    count: int


# Question generation request
class QuestionGenerateRequest(BaseModel):
    topic_id: int
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    count: int = Field(default=5, ge=1, le=10)


# Question response (without correct answer for quiz)
class QuestionResponse(BaseModel):
    question_id: int
    topic_id: Optional[int] = None
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str
    created_at: datetime

    class Config:
        from_attributes = True


# Question with answer (for solution view)
class QuestionWithAnswerResponse(BaseModel):
    question_id: int
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str
    created_at: datetime

    class Config:
        from_attributes = True


# Question generation response
class QuestionGenerateResponse(BaseModel):
    questions: List[QuestionResponse]
    topic: TopicResponse
    count: int


# Answer submission
class AnswerSubmitRequest(BaseModel):
    user_answer: str = Field(..., pattern="^[abcd]$")
    time_spent_seconds: Optional[int] = Field(default=None, ge=0)


class AnswerSubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    user_answer: str
    explanation: Optional[str] = None
    question_id: int


# Internal schema for Claude API response parsing
class ClaudeQuestionSchema(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str = Field(..., pattern="^[abcd]$")
    explanation: str
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
