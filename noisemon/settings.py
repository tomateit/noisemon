from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )
    DATABASE_URI: str
    TIMEZONE: str = "UTC"
    ENVIRONMENT: str = "development"
    TEXT_VECTORIZATION_MODEL_NAME: str = "Jean-Baptiste/roberta-large-ner-english"

settings = Settings()
