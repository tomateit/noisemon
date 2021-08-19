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
    HOST: str = "127.0.0.1"
    PORT: int = 8012
    ENVIRONMENT: str = "development"
    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str
    
    class Config:
        case_sensitive = True
        _env_file=env_location,
        _env_file_encoding="utf-8"

    class TelegramConfig:
        @staticmethod
        def get_channels_list() -> List[str]:
            channels_list = []
            with open("telegram_channels.txt", "r", encoding="UTF8") as chs:
                for line in chs:
                    channels_list.append(line.strip())
            return channels_list




settings = Settings()
