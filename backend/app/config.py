from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/money"

    # JWT - MUST be set in environment
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS - comma-separated allowed origins
    allowed_origins: str = "http://localhost:5173,https://www.bestddr.com"

    model_config = {"env_file": "../.env"}


settings = Settings()
