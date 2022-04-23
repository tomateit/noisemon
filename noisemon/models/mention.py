from __future__ import annotations
from typing import List, Optional, Tuple, Set, Any
from datetime import datetime
from collections import Counter
from functools import lru_cache

import uuid
import sqlalchemy
import numpy as np
from sqlalchemy import select
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Enum, DateTime, LargeBinary
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import BYTEA

from database import Base
from schemas import EntityType
from .entity import Entity
from .document import Document


def generate_uuid():
    return str(uuid.uuid4())

class NumpyNDArrayFloat32AsBytes(TypeDecorator):
    impl = BYTEA
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            shape = value.shape
            value = value.astype(np.float32).reshape((max(shape),)).tobytes()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = np.frombuffer(value, np.float32)
            shape = value.shape
            value = value.reshape((max(shape),))
        return value


class Mention(Base):
    __tablename__ = "mentions"
    mention_id = Column(String, name="id", primary_key=True, default=generate_uuid)
    entity_qid = Column(String, ForeignKey("entities.qid"), name="entity_qid", nullable=False)
    origin_id = Column(String, ForeignKey("documents.id"), name="origin_id", nullable=False)
    # timestamp = Column(DateTime, nullable=False)

    entity = relationship("Entity", back_populates="mentions")
    origin = relationship("Document", back_populates="mentions")

    span = Column(String, name="span", nullable=False) # textual form
    span_start = Column(Integer, name="span_start", nullable=False)
    span_end = Column(Integer, name="span_end", nullable=False)
    
    vector_index = Column(Integer, name="vector_index", primary_key=True, nullable=True, default=None) # integer that match vector in faiss index
    vector = Column(NumpyNDArrayFloat32AsBytes, name="vector", nullable=False) # numpy (d,) vector as bytes "float32"
    # metadata for analytics
    created_at = Column(DateTime, default=datetime.now, nullable=False) 
    number_of_matches = Column(Integer, name="number_of_matches", default=0, nullable=False) # how many times an entity was matched with this vector
    

    @staticmethod
    def get_all_active_vectors(db: Session) -> Optional[np.ndarray]:
        """
        Returns list of numpy vectors representing Mention.vector's of respective Vector Indices with 'index>=0', sorted in asc
        Vectors with index<0 considered as deactivated
        """
        with db.begin():
            query = select(Mention).where(Mention.vector_index >= 0).order_by(Mention.vector_index.asc())
            query_result = db.execute(query).scalars().all()
            # consistency check - vectors in db must have indices like 0,1,2,3,4,5... otherwise faiss indices will not map
            list_of_retrieved_indices = sorted([int(x.vector_index) for x in query_result])
            assert list_of_retrieved_indices == list(range(len(query_result))), "Retrieved Mention indices must be consequential as 0...len(vecs)"

            query_result = [x.vector for x in query_result]
            if query_result:
                return np.vstack(query_result)
            else:
                return None

    @staticmethod
    def get_by_vector_index(db: Session, index: int) -> Optional[Mention]:
        if db.in_transaction():
            db.commit()
        with db.begin():
            statement = (select(Mention)
                .filter_by(vector_index=index))
            mention = db.execute(statement).scalars().first()
        return mention

    @staticmethod
    def get_all_mentioned_qids(db: Session) -> List[str]:
        query = select(Mention.entity_qid).distinct()
        result = db.execute(query).scalars().all()
        db.commit()
        return result


    @staticmethod
    def increment_number_of_mentions(db: Session, mention_model: Mention):
        with db.begin_nested():
            mention_model.number_of_matches += 1

    def __repr__(self):
        return f"Mention[span={self.span},qid={self.entity_qid}]"