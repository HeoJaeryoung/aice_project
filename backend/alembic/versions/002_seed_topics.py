"""Seed initial topics

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert initial topics for AICE Associate exam
    op.execute("""
        INSERT INTO topics (name, code, description, display_order) VALUES
        ('AI 기초', 'AI_BASIC', 'AI의 기본 개념, 역사, 응용 분야', 1),
        ('머신러닝', 'ML', '지도학습, 비지도학습, 강화학습의 기본 개념', 2),
        ('딥러닝', 'DL', '신경망의 구조, 활성화 함수, 역전파', 3),
        ('CNN', 'CNN', '합성곱 신경망, 이미지 처리, 컴퓨터 비전', 4),
        ('RNN', 'RNN', '순환 신경망, LSTM, GRU, 시계열 데이터', 5),
        ('자연어처리', 'NLP', '텍스트 전처리, 워드 임베딩, Transformer', 6),
        ('데이터 전처리', 'DATA_PREP', '데이터 정제, 정규화, 특성 엔지니어링', 7),
        ('모델 평가', 'EVALUATION', '정확도, 정밀도, 재현율, F1 스코어, ROC-AUC', 8)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM topics WHERE code IN ('AI_BASIC', 'ML', 'DL', 'CNN', 'RNN', 'NLP', 'DATA_PREP', 'EVALUATION')")
