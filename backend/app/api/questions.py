from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Topic, Question, User, UserAnswer, MistakeNote
from app.schemas import (
    TopicResponse,
    TopicListResponse,
    QuestionGenerateRequest,
    QuestionResponse,
    QuestionWithAnswerResponse,
    QuestionGenerateResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
)
from app.api.deps import get_current_user
from app.services import openai_service

router = APIRouter(prefix="/api/questions", tags=["Questions"])


@router.get("/topics", response_model=TopicListResponse)
async def get_topics(
    db: AsyncSession = Depends(get_db),
):
    """주제 목록 조회"""
    result = await db.execute(
        select(Topic)
        .where(Topic.is_active == True)
        .order_by(Topic.display_order)
    )
    topics = result.scalars().all()

    return TopicListResponse(
        topics=[TopicResponse.model_validate(t) for t in topics],
        count=len(topics),
    )


@router.post("/generate", response_model=QuestionGenerateResponse)
async def generate_questions(
    request: QuestionGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI 문제 생성"""
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
            count=request.count,
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

    await db.commit()

    # Refresh to get IDs
    for q in saved_questions:
        await db.refresh(q)

    return QuestionGenerateResponse(
        questions=[QuestionResponse.model_validate(q) for q in saved_questions],
        topic=TopicResponse.model_validate(topic),
        count=len(saved_questions),
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문제 조회 (정답 제외)"""
    result = await db.execute(
        select(Question).where(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    return QuestionResponse.model_validate(question)


@router.post("/{question_id}/answer", response_model=AnswerSubmitResponse)
async def submit_answer(
    question_id: int,
    request: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """답안 제출"""
    # Get question
    result = await db.execute(
        select(Question).where(Question.question_id == question_id)
    )
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    # Check answer
    is_correct = request.user_answer.lower() == question.correct_answer.lower()

    # Save user answer
    user_answer = UserAnswer(
        user_id=current_user.user_id,
        question_id=question_id,
        user_answer=request.user_answer.lower(),
        is_correct=is_correct,
        time_spent_seconds=request.time_spent_seconds,
    )
    db.add(user_answer)

    # Update question used count
    question.used_count += 1

    # If wrong, add to mistake notes
    if not is_correct:
        # Check if already in mistake notes
        result = await db.execute(
            select(MistakeNote).where(
                MistakeNote.user_id == current_user.user_id,
                MistakeNote.question_id == question_id,
            )
        )
        existing_note = result.scalar_one_or_none()

        if existing_note:
            existing_note.mistake_count += 1
            existing_note.last_mistake_at = user_answer.answered_at
        else:
            mistake_note = MistakeNote(
                user_id=current_user.user_id,
                question_id=question_id,
            )
            db.add(mistake_note)

    await db.commit()

    return AnswerSubmitResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        user_answer=request.user_answer.lower(),
        explanation=question.explanation,
        question_id=question_id,
    )


@router.get("/{question_id}/solution", response_model=QuestionWithAnswerResponse)
async def get_solution(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """해설 조회 (정답 포함)"""
    result = await db.execute(
        select(Question, Topic)
        .outerjoin(Topic, Question.topic_id == Topic.topic_id)
        .where(Question.question_id == question_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    question, topic = row

    return QuestionWithAnswerResponse(
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
    )
