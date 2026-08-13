from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    assistant_database_url: str = "sqlite:///./assistant.db"
    jwt_secret: str = "change-me-local-only"
    jwt_algorithm: str = "HS256"

    # Hosted Hugging Face Inference Providers configuration.
    # HF_TOKEN is intentionally supplied only at runtime (local .env / Jenkins credential / AWS Secrets Manager).
    hf_token: str = ""
    assistant_model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    assistant_provider: str = "auto"
    assistant_backend: str = "huggingface"
    assistant_require_llm: bool = True
    assistant_api_timeout_seconds: float = 45.0
    assistant_max_retries: int = 2
    assistant_retry_backoff_seconds: float = 1.0
    assistant_max_new_tokens: int = 220
    assistant_temperature: float = 0.2
    assistant_top_p: float = 0.9

    assistant_max_history_messages: int = 8
    assistant_top_k_context: int = 3
    assistant_max_input_chars: int = 4000
    knowledge_path: str = str(Path(__file__).resolve().parents[1] / "knowledge" / "campus_knowledge.json")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return self.assistant_database_url


settings = Settings()
