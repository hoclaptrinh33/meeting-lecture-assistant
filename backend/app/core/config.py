from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Postgres
    POSTGRES_DB: str = "meeting"
    POSTGRES_USER: str = "meeting"
    POSTGRES_PASSWORD: str = "meeting"
    DATABASE_URL: str = "postgresql+psycopg://meeting:meeting@localhost:5432/meeting"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth & Tokens
    JWT_SECRET: str = "default_secret_key_needs_to_be_at_least_32_bytes_long"
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7

    # Hugging Face
    HF_TOKEN: Optional[str] = None
    HF_HOME: str = "/cache/huggingface"

    # Whisper
    WHISPER_MODEL: str = "large-v3-turbo"
    WHISPER_DRAFT_MODEL: str = "small"
    WHISPER_DEVICE: str = "cuda"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_BEAM_SIZE: int = 5
    WHISPER_DRAFT_BEAM_SIZE: int = 1

    # LLM
    LLM_BASE_URL: str = "http://host.docker.internal:11434/v1"
    LLM_API_KEY: Optional[str] = "none"
    LLM_MODEL: Optional[str] = None
    LLM_TIMEOUT_SECONDS: int = 120
    LLM_JSON_MODE: bool = True

    # Storage & Limits
    DATA_DIR: str = "/data"
    MAX_DURATION_SECONDS: int = 10800  # 3 hours
    MAX_OPUS_BYTES: int = 67108864     # 64 MB
    MAX_ORIGINAL_BYTES: int = 524288000 # 500 MB

    # GPU
    CUDA_VISIBLE_DEVICES: str = "0"
    PYTORCH_CUDA_ALLOC_CONF: str = "expandable_segments:True"

    # Voice Profile
    VOICE_MATCH_THRESHOLD: float = 0.75
    VOICE_MATCH_MARGIN: float = 0.05


settings = Settings()
