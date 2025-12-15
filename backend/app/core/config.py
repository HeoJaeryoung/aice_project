from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AICE Master"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/aice_master"

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Claude API
    ANTHROPIC_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
