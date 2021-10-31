from typing import List, Optional, Tuple, Set, Any
from datetime import datetime
from collections import Counter

import uuid
import sqlalchemy
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Enum, BLOB, DateTime
from sqlalchemy.orm import relationship

from database import Base
from schemas import EntityType


def generate_uuid():
    return str(uuid.uuid4())


class VectorIndex(Base):
    __tablename__ = "vector_indices"
    # main data
    vector_id = Column(String, name="id", primary_key=True, default=generate_uuid) # unique index in database
    index = Column(Integer, name="index", primary_key=True) # integer that match vector in faiss index
    entity_qid = Column(String, ForeignKey("entities.qid"), nullable=False) # matching entity qid
    vector = Column(BLOB, name="vector", nullable=False) # numpy (d,) vector as bytes "float32"
    # metadata for analytics
    source = Column(String, name="source", nullable=False) # origin of the vector: dataset or detected online
    created_at = Column(DateTime, default=datetime.now, nullable=False) 
    number_of_matches = Column(Integer, name="number_of_matches", default=0, nullable=False) # how many times an entity was matched with this vector
    span = Column(String, name="span", nullable=False) # textual form
    
    entity = relationship("Entity", back_populates="associated_vector_indices") 

    @staticmethod
    def get_major(x) -> Tuple[Any, int]:
        """
        Returns the leftmost VectorIndex with most frequent entity_qid and its respective count 
        """
        qids = [y.entity_qid for y in x]
        QID, count = Counter(qids).most_common(1)[0]
        for y in x:
            if y.entity_qid == QID:
                return y, count
        raise Exception("WTF")



class Entity(Base):
    __tablename__ = "entities"
    qid = Column(String, name="qid", primary_key=True)
    name = Column(String, unique=False, nullable=False)
    type = Column(Enum(EntityType), nullable=False)
    
    mentions = relationship("Mention", back_populates="entity")
    associated_vector_indices = relationship("VectorIndex", back_populates="entity")
    @property
    def aliases(self) -> Set[str]:
        return set([x.span for x in self.associated_vector_indices])


class Mention(Base):
    __tablename__ = "mentions"
    mention_id = Column(String, name="id", primary_key=True, default=generate_uuid)
    source = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    entity_qid = Column(String, ForeignKey("entities.qid"), nullable=False)

    entity = relationship("Entity", back_populates="mentions")

