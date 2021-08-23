from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime
from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
import uuid

from schemas import EntityType

def generate_uuid():
    return str(uuid.uuid4())



class Entity(Base):
    __tablename__ = "entities"
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    name = Column(String, unique=False, index=True)
    type = Column(Enum(EntityType))
    mentions = relationship("Mention", back_populates="entity")

class Mention(Base):
    __tablename__ = "mentions"
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    source = Column(String)
    timestamp = Column(TIMESTAMP)
    
    entity_id = Column(String, ForeignKey("entities.id"))
    entity = relationship("Entity", back_populates="mentions")


