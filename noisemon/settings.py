from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8012
    ENVIRONMENT: str = "development"
    
    class TelegramConfig:
        @staticmethod
        def get_channels_list() -> List[str]:
            channels_list = []
            with open("telegram_channels.txt", "r", encoding="UTF8") as chs:
                for line in chs:
                    channels_list.append(line.strip())
            return channels_list



settings = Settings(
    _env_file=".env",
    _env_file_encoding="utf-8"
)