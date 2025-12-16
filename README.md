# AICE Master - AI 기반 자격증 학습 플랫폼

AICE Associate 자격증 수험생을 위한 AI 기반 학습 플랫폼입니다.
OpenAI GPT를 활용하여 무한한 연습 문제를 생성하고, 개인별 학습 통계와 오답 관리 기능을 제공합니다.

## 주요 기능

- **AI 문제 생성**: GPT-4를 활용한 AICE 시험 스타일 문제 자동 생성
- **8개 주제 지원**: AI 기초, 머신러닝, 딥러닝, CNN, RNN, 자연어처리, 데이터 전처리, 모델 평가
- **3단계 난이도**: 쉬움, 보통, 어려움
- **즉시 채점**: 정답/오답 판정 및 상세 해설 제공
- **오답노트**: 틀린 문제 자동 저장 및 복습
- **학습 통계**: 정답률, 주제별 분석, 주간 학습 현황

## 기술 스택

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- JWT 인증
- OpenAI API

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Zustand (상태 관리)
- React Router v6

### Infrastructure
- Docker + Docker Compose
- PostgreSQL 15

## 프로젝트 구조

```
aice_project/
├── backend/
│   ├── app/
│   │   ├── api/           # API 라우터
│   │   ├── core/          # 설정, DB, 보안
│   │   ├── models/        # SQLAlchemy 모델
│   │   ├── schemas/       # Pydantic 스키마
│   │   ├── services/      # 비즈니스 로직
│   │   └── main.py        # FastAPI 앱
│   ├── alembic/           # DB 마이그레이션
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── services/      # API 서비스
│   │   ├── stores/        # Zustand 스토어
│   │   ├── types/         # TypeScript 타입
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 시작하기

### 사전 요구사항

- Docker & Docker Compose
- OpenAI API Key

### 1. 환경 변수 설정

```bash
cd backend
cp .env.example .env
```

`.env` 파일을 열고 OpenAI API 키를 설정합니다:

```env
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET_KEY=your-secure-secret-key
```

### 2. Docker로 실행

```bash
# 프로젝트 루트에서
docker-compose up -d
```

### 3. 데이터베이스 마이그레이션

```bash
docker-compose exec backend alembic upgrade head
```

### 4. 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 로컬 개발 환경

### Backend

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# PostgreSQL 실행 (Docker)
docker-compose up -d db

# 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

## API 엔드포인트

### 인증 (`/api/auth`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/register` | 회원가입 |
| POST | `/login` | 로그인 |
| GET | `/me` | 내 정보 조회 |
| POST | `/logout` | 로그아웃 |

### 문제 (`/api/questions`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/topics` | 주제 목록 |
| POST | `/generate` | AI 문제 생성 |
| GET | `/{id}` | 문제 조회 |
| POST | `/{id}/answer` | 답안 제출 |
| GET | `/{id}/solution` | 해설 조회 |

### 학습 (`/api/study`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/sessions` | 세션 시작 |
| PUT | `/sessions/{id}` | 세션 종료 |
| GET | `/sessions` | 세션 목록 |
| GET | `/mistakes` | 오답 목록 |
| GET | `/history` | 학습 기록 |

### 대시보드 (`/api/dashboard`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/summary` | 학습 요약 |
| GET | `/stats/topics` | 주제별 통계 |
| GET | `/stats/weekly` | 주간 통계 |

## 라이선스

MIT License
