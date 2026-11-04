# from functools import lru_cache
# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     llm_provider: str = "ollama"
#     ollama_base_url: str = "http://localhost:11434"
#     ollama_model: str = "granite3.3:8b"
#     database_url: str = "postgresql+psycopg://agent_reader:reader_change_me@localhost:5432/ecommerce_db"
#     owner_database_url: str = "postgresql+psycopg://app_user:change_me@localhost:5432/ecommerce_db"
#     app_max_web_bytes: int = 1_500_000
#     app_max_web_chars: int = 18_000
#     app_http_timeout: float = 12.0
#     app_sql_timeout_ms: int = 5_000
#     app_sql_max_rows: int = 100
#     app_log_level: str = "INFO"
#     model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# @lru_cache(maxsize=1)
# def get_settings() -> Settings:
#     return Settings()

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "granite3.3:8b"

    database_url: str = (
        "postgresql+psycopg://agent_reader:reader_change_me"
        "@localhost:5432/ecommerce_db"
    )
    owner_database_url: str = (
        "postgresql+psycopg://app_user:change_me"
        "@localhost:5432/ecommerce_db"
    )

    # Web search
    tavily_api_key: str = "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"

    # Existing application settings
    app_max_web_bytes: int = 1_500_000
    app_max_web_chars: int = 18_000
    app_http_timeout: float = 12.0
    app_sql_timeout_ms: int = 5_000
    app_sql_max_rows: int = 100
    app_log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
