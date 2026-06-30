from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from the .env file.
    """

    # ----------------------------
    # Application
    # ----------------------------
    APP_NAME: str = "ClaimPilot API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    # ----------------------------
    # Server
    # ----------------------------
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # ----------------------------
    # Security
    # ----------------------------
    SECRET_KEY: str

    # ----------------------------
    # Supabase
    # ----------------------------
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # ----------------------------
    # Groq AI
    # ----------------------------
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()