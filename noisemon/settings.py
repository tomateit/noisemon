from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URI: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    RABBITMQ_URI: str
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_EXCHANGE: str
    RABBITMQ_SOURCE_QUEUE: str
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
