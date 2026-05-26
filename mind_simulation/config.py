from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # config — overridable via MIND_* env vars
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.2
    max_rounds: int = 6
    max_history: int = 20  # max messages kept in chat history (2 per turn)
    prompts_dir: Path = Path(__file__).parent / "prompts"

    # secrets — no prefix, must match env var name exactly
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    langfuse_public_key: str | None = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="http://localhost:3000", alias="LANGFUSE_HOST")

    @computed_field
    @property
    def personalities_dir(self) -> Path:
        return self.prompts_dir / "sub_personalities"

    @computed_field
    @property
    def prompts_schemas_dir(self) -> Path:
        return self.prompts_dir / "schemas"

    model_config = SettingsConfigDict(env_prefix="MIND_", env_file=".env", populate_by_name=True)


settings = Settings()
