from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://smm:smm_secret@localhost:5432/smm_panel"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TELEGRAM_BOT_TOKEN: str = ""
    SMMWIZ_API_URL: str = "https://smmwiz.com/api/v2"
    SMMWIZ_API_KEY: str = ""
    PRM4U_API_URL: str = "https://prm4u.com/api/v2"
    PRM4U_API_KEY: str = ""
    REFERRAL_COMMISSION_RATE: float = 0.05
    FRONTEND_URL: str = "http://localhost:5173"
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    FLUTTERWAVE_SECRET_KEY: str = ""
    FLUTTERWAVE_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
