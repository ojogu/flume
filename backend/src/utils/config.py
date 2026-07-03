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
    api_url:str
    celery_beat_interval:int
    encryption_key:str
    celery_broker_url:str
    celery_result_backend:str
    telegram_key:str
    client_id:str
    client_secret:str
    redirect_url:str
    resend_key:str
    resend_mail:str
    api_key_prefix:str
    app_env:str = "dev"
    cloudflare_key: str | None = None
    cloudflare_api_token: str | None = None
    cloudflare_token_value: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    s3_url: str | None = None
    r2_bucket_name: str = "flume-uploads"

    # ── yt-dlp / workspace configuration ──────────────────────────────────
    # base directory for per-job workspaces; each job gets its own subdirectory
    # e.g. /var/lib/flume/workspaces/job_<short_uuid>/
    workspaces_dir: str = "/var/lib/flume/workspaces"
    # optional cookies file for yt-dlp (authenticated downloads — private content, age-restricted, etc.)
    ytdlp_cookie_file: str | None = None
    # hard limit on downloaded file size (bytes); jobs exceeding this are failed.
    # default: 2 GB
    max_download_size_bytes: int = 2_147_483_648

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",  # Adjusted to point to the root directory
        env_file_encoding="utf-8",
    )

config = Config()

# Static route/version constants separate from env-sensitive Config
class Settings:
    PROJECT_NAME: str = "Flume"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "API for Flume; a media processor"