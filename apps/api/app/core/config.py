from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "TeleDerma"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./telederma.db"
    frontend_url: str = "http://localhost:3000"
    session_cookie_name: str = "telederma_session"
    session_expiry_days: int = 30
    model_name: str = "dima806/skin_types_image_detection"
    model_license: str = "Apache-2.0"
    model_revision: str = "main"
    max_upload_mb: int = 5
    rate_limit_per_minute: int = 60
    redis_url: str | None = None
    payment_provider: str = "none"
    payment_keys: str | None = None
    version: str = "0.1.0"

    class Config:
        env_file = ".env"
        env_prefix = "TELEDERMA_"


settings = Settings()
