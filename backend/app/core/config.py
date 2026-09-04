from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./arvya.db"
    jwt_secret: str = "arvya-demo-secret-change-in-production"
    frontend_origin: str = "http://localhost:5173"
    razorpay_key_id: str | None = None
    razorpay_key_secret: str | None = None
    razorpay_webhook_secret: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    # Read current local Test Mode configuration for each integration request so a demo
    # user can add keys without having to clear an in-memory settings cache.
    return Settings()


def get_database_url() -> str:
    """Normalize common managed-Postgres URLs for SQLAlchemy's psycopg driver."""
    database_url = get_settings().database_url
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def get_frontend_origins() -> list[str]:
    """Return the configured browser origins, accepting a comma-separated allow-list."""
    origins = [
        origin.strip().rstrip("/")
        for origin in get_settings().frontend_origin.split(",")
        if origin.strip()
    ]
    return origins or ["http://localhost:5173"]
