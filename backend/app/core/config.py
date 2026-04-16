import json
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    google_genai_use_vertexai: bool = False
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"

    docs_dir: str = "./docs"
    vector_store_path: str = "./.lancedb"
    embedding_provider: str = "gemini"
    gemini_embedding_model: str = "gemini-embedding-001"

    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str] | Any:
        if not isinstance(value, str):
            return value

        raw_value = value.strip()
        if not raw_value:
            return []

        try:
            parsed_value = json.loads(raw_value)
        except json.JSONDecodeError:
            if raw_value.startswith("[") and raw_value.endswith("]"):
                raw_value = raw_value[1:-1]
            return [
                origin.strip().strip('"').strip("'")
                for origin in raw_value.split(",")
                if origin.strip()
            ]

        if isinstance(parsed_value, str):
            return [parsed_value]
        return parsed_value

    model_config = {
        "env_file": ("../.env", ".env"),
        "env_file_encoding": "utf-8",
    }
