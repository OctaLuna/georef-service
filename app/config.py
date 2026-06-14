import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8001
    geojson_path: str = "data/bolivia.geojson"
    allowed_origins: list[str] = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]


settings = Settings()
