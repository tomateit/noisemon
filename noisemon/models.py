from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime
from database import Base
import sqlalchemy
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Enum, BLOB, DateTime
from sqlalchemy.orm import relationship

import uuid

from schemas import EntityType

def generate_uuid():
    return str(uuid.uuid4())


class VectorIndex(Base):
    __tablename__ = "vector_indices"
    vector_id = Column(String, name="id", primary_key=True, default=generate_uuid)
    index = Column(Integer, name="index", primary_key=True) # integer that match vector in faiss index
    entity_qid = Column(String, ForeignKey("entities.qid")) # matching entity qid
    span = Column(String, name="span") # textual form
    source = Column(String, name="source") # origin of the vector: dataset or detected online
    created_at = Column(DateTime, default=datetime.now)
    vector = Column(BLOB, name="vector")
    

class Entity(Base):
    __tablename__ = "entities"
    qid = Column(String, name="qid", primary_key=True)
    name = Column(String, unique=False)
    type = Column(Enum(EntityType))
    mentions = relationship("Mention", back_populates="entity")


class Mention(Base):
    __tablename__ = "mentions"
    mention_id = Column(String, name="id", primary_key=True, default=generate_uuid)
    source = Column(String)
    timestamp = Column(TIMESTAMP)
    entity_qid = Column(String, ForeignKey("entities.qid"))
    vector_id = Column(String, ForeignKey("vector_indices.id"))

    entity = relationship("Entity", back_populates="mentions")



