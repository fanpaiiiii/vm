from pydantic_settings import BaseSettings
from typing import List
import json
import os
import secrets


class Settings(BaseSettings):
    APP_NAME: str = "外贸团队协作工具 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./trade_team.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:3006","http://154.219.108.60","http://154.219.108.60:3006"]'
    FRANKFURTER_API_URL: str = "https://api.frankfurter.app"

    # Rate limiting
    RATE_LIMIT: str = "100/minute"

    @property
    def cors_origins_list(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:5173", "http://localhost:3006"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
