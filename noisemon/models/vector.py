from __future__ import annotations
from typing import List, Optional, Tuple, Set, Any
from datetime import datetime
from collections import Counter
from functools import lru_cache

import uuid
import sqlalchemy
import numpy as np
from sqlalchemy import select
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Enum, BLOB, DateTime
from sqlalchemy.orm import relationship, Session

from database import Base
from schemas import EntityType


def generate_uuid():
    return str(uuid.uuid4())


class VectorIndexModel(Base):
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
    def get_all_active_vectors(db: Session) -> np.ndarray:
        """
        Returns list of numpy vectors representing VectorIndexModel.vector's of respective Vector Indices with 'index>=0', sorted in asc
        """
        with db.begin():
            query = select(VectorIndexModel).where(VectorIndexModel.index >= 0).order_by(VectorIndexModel.index.asc())
            query_result = db.execute(query).scalars().all()
            # consistency check - vectors in db must have indices like 0,1,2,3,4,5... otherwise faiss indices will not map
            list_of_retrieved_indices = sorted([int(x.index) for x in query_result])
            assert list_of_retrieved_indices == list(range(len(query_result))), "Retrieved VectorIndexModel indices must be consequential as 0...len(vecs)"

            query_result = list(map(lambda x: np.frombuffer(x.vector, dtype="float32"), query_result))
            # db.commit()
        return np.vstack(query_result)

    @staticmethod
    def get_vector_model_by_index(db: Session, index: int) -> Optional[VectorIndexModel]:
        if db.in_transaction():
            db.commit()
        with db.begin():
            statement = (select(VectorIndexModel)
                .filter_by(index=index))
            vector_index = db.execute(statement).scalars().first()
        return vector_index

    @staticmethod
    def get_all_vector_index_qids(db: Session) -> List[str]:
        query = select(VectorIndexModel.entity_qid).distinct()
        result = db.execute(query).scalars().all()
        db.commit()
        return result

    def create_vector_index(db: Session, entity_qid:str, index: int, span: str, source: str, vector: np.ndarray) -> VectorIndexModel:
        if db.in_transaction():
            db.commit()
        with db.begin():
            vector_index = VectorIndexModel(
                index=index, 
                entity_qid=entity_qid, 
                vector=vector,
                span=span, 
                source=source,
            )
            db.add(vector_index)
        return vector_index

    @staticmethod
    def increment_number_of_mentions(db: Session, vector_index: VectorIndexModel):
        if db.in_transaction():
            db.commit()
        with db.begin():
            vector_index.number_of_matches += 1

    def __repr__(self):
        return f"VectorIndex[span={self.span},qid={self.entity_qid}]"