from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Tuple, Union
from datetime import datetime
from database import Base

class DataChunk(BaseModel):
    # origin: str
    link: str
    text: str
    raw_text: str
    timestamp: str # datetime is not json serializable

    # class Config:
    #     orm_mode = True

class EntityType(str, Enum):
    ORGANIZATION = "ORG"

class Entity(BaseModel):
    name: str
    type: EntityType

