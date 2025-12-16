from datetime import date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel


# Summary response
class DashboardSummaryResponse(BaseModel):
    total_questions: int
    total_correct: int
    accuracy_rate: Optional[Decimal] = None
    total_sessions: int
    total_study_time_seconds: int
    current_streak: int
    mistake_count: int


# Topic stats
class TopicStatResponse(BaseModel):
    topic_id: int
    topic_name: str
    topic_code: Optional[str] = None
    total_questions: int
    correct_answers: int
    accuracy_rate: Optional[Decimal] = None


class TopicStatsResponse(BaseModel):
    stats: List[TopicStatResponse]
    count: int


# Weekly stats
class DailyStatResponse(BaseModel):
    date: date
    questions_count: int
    correct_count: int
    accuracy_rate: Optional[Decimal] = None


class WeeklyStatsResponse(BaseModel):
    daily_stats: List[DailyStatResponse]
    total_questions: int
    total_correct: int
    average_accuracy: Optional[Decimal] = None
