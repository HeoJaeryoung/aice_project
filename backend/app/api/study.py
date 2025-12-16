from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Topic, Question, User, StudySession, UserAnswer, MistakeNote
from app.schemas import (
    TopicResponse,
    QuestionWithAnswerResponse,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionQuestionResponse,
    SessionResponse,
    SessionResultResponse,
    SessionListResponse,
    MistakeNoteResponse,
    MistakeListResponse,
    StudyHistoryResponse,
)
from app.api.deps import get_current_user
from app.services import openai_service

router = APIRouter(prefix="/api/study", tags=["Study"])


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(
    request: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """학습 세션 시작"""
    # Get topic
    result = await db.execute(
        select(Topic).where(Topic.topic_id == request.topic_id)
    )
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Generate questions using OpenAI GPT API
    try:
        generated = await openai_service.generate_questions(
            topic_name=topic.name,
            difficulty=request.difficulty,
            count=request.question_count,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    if not generated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questions",
        )

    # Save questions to database
    saved_questions = []
    for q in generated:
        question = Question(
            topic_id=topic.topic_id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            difficulty=q.difficulty,
            source="gpt",
        )
        db.add(question)
        saved_questions.append(question)

    await db.flush()

    # Create study session
    session = StudySession(
        user_id=current_user.user_id,
        topic_id=topic.topic_id,
        difficulty=request.difficulty,
        question_count=len(saved_questions),
        status="active",
    )
    db.add(session)

    await db.commit()
    await db.refresh(session)

    for q in saved_questions:
        await db.refresh(q)

    return SessionCreateResponse(
        session_id=session.session_id,
        topic=TopicResponse.model_validate(topic),
        difficulty=request.difficulty,
        question_count=len(saved_questions),
        questions=[SessionQuestionResponse.model_validate(q) for q in saved_questions],
        started_at=session.started_at,
    )


@router.put("/sessions/{session_id}", response_model=SessionResultResponse)
async def end_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """학습 세션 종료"""
    # Get session
    result = await db.execute(
        select(StudySession).where(
            StudySession.session_id == session_id,
            StudySession.user_id == current_user.user_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already ended",
        )

    # Calculate session stats
    result = await db.execute(
        select(
            func.count(UserAnswer.answer_id).label("attempted"),
            func.sum(func.cast(UserAnswer.is_correct, Integer)).label("correct"),
        ).where(UserAnswer.session_id == session_id)
    )
    stats = result.first()

    attempted = stats.attempted or 0
    correct = stats.correct or 0

    # Update session
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
    session.questions_attempted = attempted
    session.correct_answers = correct
    session.accuracy_rate = Decimal(correct / attempted * 100) if attempted > 0 else None

    await db.commit()
    await db.refresh(session)

    return SessionResultResponse(
        session_id=session.session_id,
        status=session.status,
        questions_attempted=session.questions_attempted,
        correct_answers=session.correct_answers,
        accuracy_rate=session.accuracy_rate,
        duration_seconds=session.duration_seconds,
        ended_at=session.ended_at,
    )


@router.get("/sessions", response_model=SessionListResponse)
async def get_sessions(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """학습 세션 목록 조회"""
    result = await db.execute(
        select(StudySession, Topic)
        .outerjoin(Topic, StudySession.topic_id == Topic.topic_id)
        .where(StudySession.user_id == current_user.user_id)
        .order_by(StudySession.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()

    sessions = []
    for session, topic in rows:
        sessions.append(SessionResponse(
            session_id=session.session_id,
            topic_id=session.topic_id,
            topic_name=topic.name if topic else None,
            difficulty=session.difficulty,
            question_count=session.question_count,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_seconds=session.duration_seconds,
            questions_attempted=session.questions_attempted,
            correct_answers=session.correct_answers,
            accuracy_rate=session.accuracy_rate,
        ))

    return SessionListResponse(
        sessions=sessions,
        count=len(sessions),
    )


@router.get("/mistakes", response_model=MistakeListResponse)
async def get_mistakes(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    mastered: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """오답노트 목록 조회"""
    query = (
        select(MistakeNote, Question, Topic)
        .join(Question, MistakeNote.question_id == Question.question_id)
        .outerjoin(Topic, Question.topic_id == Topic.topic_id)
        .where(MistakeNote.user_id == current_user.user_id)
    )

    if mastered is not None:
        query = query.where(MistakeNote.mastered == mastered)

    query = query.order_by(MistakeNote.last_mistake_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    rows = result.all()

    mistakes = []
    for note, question, topic in rows:
        mistakes.append(MistakeNoteResponse(
            note_id=note.note_id,
            question=QuestionWithAnswerResponse(
                question_id=question.question_id,
                topic_id=question.topic_id,
                topic_name=topic.name if topic else None,
                question_text=question.question_text,
                option_a=question.option_a,
                option_b=question.option_b,
                option_c=question.option_c,
                option_d=question.option_d,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                difficulty=question.difficulty,
                created_at=question.created_at,
            ),
            mistake_count=note.mistake_count,
            first_mistake_at=note.first_mistake_at,
            last_mistake_at=note.last_mistake_at,
            review_count=note.review_count,
            last_review_at=note.last_review_at,
            mastered=note.mastered,
        ))

    return MistakeListResponse(
        mistakes=mistakes,
        count=len(mistakes),
    )


@router.get("/history", response_model=StudyHistoryResponse)
async def get_history(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """학습 기록 조회"""
    # Get recent sessions
    result = await db.execute(
        select(StudySession, Topic)
        .outerjoin(Topic, StudySession.topic_id == Topic.topic_id)
        .where(
            StudySession.user_id == current_user.user_id,
            StudySession.status == "completed",
        )
        .order_by(StudySession.ended_at.desc())
        .limit(limit)
    )
    rows = result.all()

    sessions = []
    for session, topic in rows:
        sessions.append(SessionResponse(
            session_id=session.session_id,
            topic_id=session.topic_id,
            topic_name=topic.name if topic else None,
            difficulty=session.difficulty,
            question_count=session.question_count,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_seconds=session.duration_seconds,
            questions_attempted=session.questions_attempted,
            correct_answers=session.correct_answers,
            accuracy_rate=session.accuracy_rate,
        ))

    # Get overall stats
    result = await db.execute(
        select(
            func.count(StudySession.session_id).label("total_sessions"),
            func.sum(StudySession.questions_attempted).label("total_questions"),
            func.sum(StudySession.correct_answers).label("total_correct"),
        ).where(
            StudySession.user_id == current_user.user_id,
            StudySession.status == "completed",
        )
    )
    stats = result.first()

    total_sessions = stats.total_sessions or 0
    total_questions = stats.total_questions or 0
    total_correct = stats.total_correct or 0
    overall_accuracy = Decimal(total_correct / total_questions * 100) if total_questions > 0 else None

    return StudyHistoryResponse(
        sessions=sessions,
        total_sessions=total_sessions,
        total_questions=total_questions,
        total_correct=total_correct,
        overall_accuracy=overall_accuracy,
    )
