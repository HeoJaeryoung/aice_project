from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth_router, questions_router, study_router, dashboard_router

app = FastAPI(
    title=settings.APP_NAME,
    description="AICE Associate 자격증 수험생을 위한 AI 기반 학습 플랫폼",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to AICE Master API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth_router)
app.include_router(questions_router)
app.include_router(study_router)
app.include_router(dashboard_router)
