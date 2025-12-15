"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('subscription_tier', sa.String(length=20), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('topic_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('topic_id'),
        sa.UniqueConstraint('code')
    )

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('question_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('option_a', sa.Text(), nullable=False),
        sa.Column('option_b', sa.Text(), nullable=False),
        sa.Column('option_c', sa.Text(), nullable=False),
        sa.Column('option_d', sa.Text(), nullable=False),
        sa.Column('correct_answer', sa.String(length=1), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='claude'),
        sa.Column('quality_score', sa.Numeric(precision=3, scale=2), nullable=False, server_default='4.0'),
        sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("correct_answer IN ('a', 'b', 'c', 'd')", name='check_correct_answer'),
        sa.CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name='check_difficulty'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.topic_id'], ),
        sa.PrimaryKeyConstraint('question_id')
    )
    op.create_index('idx_questions_topic', 'questions', ['topic_id'])
    op.create_index('idx_questions_difficulty', 'questions', ['difficulty'])

    # Create study_sessions table
    op.create_table(
        'study_sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('question_count', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('questions_attempted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('correct_answers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('accuracy_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.CheckConstraint("status IN ('active', 'completed', 'abandoned')", name='check_session_status'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.topic_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index('idx_sessions_user', 'study_sessions', ['user_id', 'started_at'])

    # Create user_answers table
    op.create_table(
        'user_answers',
        sa.Column('answer_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_answer', sa.String(length=1), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("user_answer IN ('a', 'b', 'c', 'd')", name='check_user_answer'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['study_sessions.session_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('answer_id')
    )
    op.create_index('idx_answers_user', 'user_answers', ['user_id', 'answered_at'])
    op.create_index('idx_answers_session', 'user_answers', ['session_id'])

    # Create mistake_notes table
    op.create_table(
        'mistake_notes',
        sa.Column('note_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('mistake_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('first_mistake_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_mistake_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_review_at', sa.DateTime(), nullable=True),
        sa.Column('mastered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mastered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('note_id'),
        sa.UniqueConstraint('user_id', 'question_id', name='uq_user_question')
    )
    op.create_index('idx_mistakes_user', 'mistake_notes', ['user_id'])


def downgrade() -> None:
    op.drop_table('mistake_notes')
    op.drop_table('user_answers')
    op.drop_table('study_sessions')
    op.drop_table('questions')
    op.drop_table('topics')
    op.drop_table('users')
