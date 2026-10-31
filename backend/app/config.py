import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Online Attendance Management System"
    secret_key: str = "dev-secret-key-super-secure-attendance-system-2026-xyz"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    database_url: str = "sqlite:///./attendance.db"
    
    # Attendance Rules
    default_attendance_threshold: float = 75.0
    allow_half_day: bool = True
    half_day_weight: float = 0.5
    
    # Institution Info
    institution_name: str = "Apex Institute of Technology"
    academic_year: str = "2025-2026"
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
