from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key:str
    jwt_algo:str 
    access_token_expiry:int
    refresh_token_expiry:int
    frontend_url:str
    celery_beat_interval:int
    encryption_key:str
    celery_broker_url:str
    celery_result_backend:str
    telegram_key:str
    client_id:str
    client_secret:str
    redirect_url:str
    app_env:str = "dev"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",  # Adjusted to point to the root directory
        env_file_encoding="utf-8",
    )

config = Config()

class Settings:
    PROJECT_NAME: str = "Flume"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "API for Flume; a media processor"
    API_V1_PREFIX: str = "/api/v1"