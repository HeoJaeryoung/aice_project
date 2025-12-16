from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, cast, Date, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Topic, Question, User, StudySession, UserAnswer, MistakeNote
from app.schemas import (
    DashboardSummaryResponse,
    TopicStatResponse,
    TopicStatsResponse,
    DailyStatResponse,
    WeeklyStatsResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """학습 요약 조회"""
    # Get total questions and correct answers
    result = await db.execute(
        select(
            func.count(UserAnswer.answer_id).label("total_questions"),
            func.sum(cast(UserAnswer.is_correct, Integer)).label("total_correct"),
        ).where(UserAnswer.user_id == current_user.user_id)
    )
    answer_stats = result.first()

    total_questions = answer_stats.total_questions or 0
    total_correct = answer_stats.total_correct or 0
    accuracy_rate = Decimal(total_correct / total_questions * 100) if total_questions > 0 else None

    # Get session stats
    result = await db.execute(
        select(
            func.count(StudySession.session_id).label("total_sessions"),
            func.coalesce(func.sum(StudySession.duration_seconds), 0).label("total_time"),
        ).where(
            StudySession.user_id == current_user.user_id,
            StudySession.status == "completed",
        )
    )
    session_stats = result.first()

    total_sessions = session_stats.total_sessions or 0
    total_study_time = session_stats.total_time or 0

    # Get mistake count
    result = await db.execute(
        select(func.count(MistakeNote.note_id)).where(
            MistakeNote.user_id == current_user.user_id,
            MistakeNote.mastered == False,
        )
    )
    mistake_count = result.scalar() or 0

    # Calculate streak (consecutive days with study sessions)
    streak = await calculate_streak(db, current_user.user_id)

    return DashboardSummaryResponse(
        total_questions=total_questions,
        total_correct=total_correct,
        accuracy_rate=accuracy_rate,
        total_sessions=total_sessions,
        total_study_time_seconds=total_study_time,
        current_streak=streak,
        mistake_count=mistake_count,
    )


async def calculate_streak(db: AsyncSession, user_id: int) -> int:
    """Calculate consecutive study days streak."""
    today = datetime.utcnow().date()
    streak = 0
    current_date = today

    while True:
        result = await db.execute(
            select(func.count(StudySession.session_id)).where(
                StudySession.user_id == user_id,
                cast(StudySession.started_at, Date) == current_date,
            )
        )
        count = result.scalar() or 0

        if count > 0:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # If today has no session, check if yesterday had one
            if current_date == today:
                current_date -= timedelta(days=1)
                continue
            break

    return streak


@router.get("/stats/topics", response_model=TopicStatsResponse)
async def get_topic_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주제별 통계 조회"""
    # Get all topics with user's stats
    result = await db.execute(
        select(
            Topic.topic_id,
            Topic.name,
            Topic.code,
            func.count(UserAnswer.answer_id).label("total_questions"),
            func.coalesce(func.sum(cast(UserAnswer.is_correct, Integer)), 0).label("correct_answers"),
        )
        .select_from(Topic)
        .outerjoin(
            UserAnswer,
            (UserAnswer.user_id == current_user.user_id) &
            (UserAnswer.question_id.in_(
                select(Question.question_id)
                .where(Question.topic_id == Topic.topic_id)
            ))
        )
        .where(Topic.is_active == True)
        .group_by(Topic.topic_id, Topic.name, Topic.code)
        .order_by(Topic.display_order)
    )

    # Get topics and calculate stats for each
    result = await db.execute(
        select(Topic).where(Topic.is_active == True).order_by(Topic.display_order)
    )
    topics = result.scalars().all()

    stats = []
    for topic in topics:
        # Get stats for each topic
        result = await db.execute(
            select(
                func.count(UserAnswer.answer_id).label("total"),
                func.coalesce(func.sum(cast(UserAnswer.is_correct, Integer)), 0).label("correct"),
            )
            .select_from(UserAnswer)
            .join(Question, UserAnswer.question_id == Question.question_id)
            .where(
                UserAnswer.user_id == current_user.user_id,
                Question.topic_id == topic.topic_id,
            )
        )
        topic_stats = result.first()

        total = topic_stats.total or 0
        correct = topic_stats.correct or 0
        accuracy = Decimal(correct / total * 100) if total > 0 else None

        stats.append(TopicStatResponse(
            topic_id=topic.topic_id,
            topic_name=topic.name,
            topic_code=topic.code,
            total_questions=total,
            correct_answers=correct,
            accuracy_rate=accuracy,
        ))

    return TopicStatsResponse(
        stats=stats,
        count=len(stats),
    )


@router.get("/stats/weekly", response_model=WeeklyStatsResponse)
async def get_weekly_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """주간 통계 조회"""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=6)

    daily_stats = []
    total_questions = 0
    total_correct = 0

    # Get stats for each day in the past week
    for i in range(7):
        current_date = week_ago + timedelta(days=i)

        result = await db.execute(
            select(
                func.count(UserAnswer.answer_id).label("questions"),
                func.coalesce(func.sum(cast(UserAnswer.is_correct, Integer)), 0).label("correct"),
            ).where(
                UserAnswer.user_id == current_user.user_id,
                cast(UserAnswer.answered_at, Date) == current_date,
            )
        )
        day_stats = result.first()

        questions = day_stats.questions or 0
        correct = day_stats.correct or 0
        accuracy = Decimal(correct / questions * 100) if questions > 0 else None

        daily_stats.append(DailyStatResponse(
            date=current_date,
            questions_count=questions,
            correct_count=correct,
            accuracy_rate=accuracy,
        ))

        total_questions += questions
        total_correct += correct

    average_accuracy = Decimal(total_correct / total_questions * 100) if total_questions > 0 else None

    return WeeklyStatsResponse(
        daily_stats=daily_stats,
        total_questions=total_questions,
        total_correct=total_correct,
        average_accuracy=average_accuracy,
    )
