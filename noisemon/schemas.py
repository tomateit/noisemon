from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Tuple
from datetime import datetime
from database import Base

class DataChunk(BaseModel):
    origin: str
    text: str
    raw_text: str

class EntityType(str, Enum):
    ORGANIZATION = "org"

class Entity(BaseModel):
    name: str
    type: EntityType



class Response(BaseModel):
    timestamp: datetime