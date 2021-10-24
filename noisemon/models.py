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


class VectorIndex(Base):
    __tablename__ = "vector_indices"
    index = Column(Integer, name="id", primary_key=True) # integer that match vector in faiss index
    entity_qid = Column(String, ForeignKey("entities.qid")) # matching entity qid
    span = Column(String, name="span", primary_key=True) # textual form
    source = Column(String, name="source", primary_key=True) # origin of the vector: dataset or detected online
    created_at = Column(TIMESTAMP, default=datetime.now)
    

class Entity(Base):
    __tablename__ = "entities"
    qid = Column(String, name="qid", primary_key=True)
    name = Column(String, unique=False, index=True)
    type = Column(Enum(EntityType))
    mentions = relationship("Mention", back_populates="entity")

class Mention(Base):
    __tablename__ = "mentions"
    mention_id = Column(String, name="id", primary_key=True, default=generate_uuid)
    source = Column(String)
    timestamp = Column(TIMESTAMP)
    entity_qid = Column(String, ForeignKey("entities.qid"))
    
    entity = relationship("Entity", back_populates="mentions")



