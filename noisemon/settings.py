from typing import List
from pydantic import BaseSettings
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

env_location = Path("./.env").resolve()
# print(env_location)
# print(Path(os.curdir).resolve())
# print("ENV111", env_location.exists())
# print(env_location.read_text())

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URI: str
    RABBITMQ_URI: str
    RABBITMQ_EXCHANGE: str
    RABBITMQ_SOURCE_QUEUE: str
    
    class Config:
        case_sensitive = True
        _env_file=env_location,
        _env_file_encoding="utf-8"


settings = Settings()
