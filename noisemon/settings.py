from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TIMEZONE: str = "UTC"
    ENVIRONMENT: str = "development"
    DATABASE_URI: str

    RABBITMQ_URI: str
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_EXCHANGE: str
    RABBITMQ_SOURCE_QUEUE: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
