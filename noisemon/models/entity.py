from pydantic import BaseModel
from enum import Enum

class EntityType(str, Enum):
    ORGANIZATION = "org"

class Entity(BaseModel):
    name: str