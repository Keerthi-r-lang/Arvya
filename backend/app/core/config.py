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
