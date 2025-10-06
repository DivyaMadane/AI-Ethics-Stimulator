from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    app_name: str = "AI Ethics Simulator API"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_ethics_sim"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()