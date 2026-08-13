from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    hf_token: str = ""
    ai_confidence_threshold: float = 0.75
    ai_model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    ai_provider: str = "auto"
    ai_backend: str = "huggingface"
    ai_require_llm: bool = True
    ai_api_timeout_seconds: float = 45.0
    ai_max_retries: int = 2
    ai_retry_backoff_seconds: float = 1.0
    ai_max_tokens: int = 180
    ai_temperature: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
