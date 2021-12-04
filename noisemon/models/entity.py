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


class Entity(Base):
    __tablename__ = "entities"
    qid = Column(String, name="qid", primary_key=True)
    name = Column(String, unique=False, nullable=False)
    type = Column(Enum(EntityType), nullable=False)
    
    mentions = relationship("Mention", back_populates="entity")
    associated_vector_indices = relationship("VectorIndexModel", back_populates="entity")

    def __repr__(self):
        return f"Entity[name={self.name},qid={self.qid}]"

    @property
    def aliases(self) -> Set[str]:
        return set([x.span for x in self.associated_vector_indices])

    @staticmethod
    def get_entities(db: Session, skip: int = 0, limit: int = 100) -> List[Entity]:
        return db.query(Entity).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_entity_qids(db: Session) -> List[str]:
        query = select(Entity.qid)
        result = db.execute(query).scalars().all()
        db.commit()
        return result

    @staticmethod
    def create_entity(db: Session, qid:str, name: str, type: EntityType) -> Entity:
        if db.in_transaction():
            db.commit()
        with db.begin():
            query = (select(Entity).filter_by(qid=qid))
            result = db.execute(query).scalars().first()
            if result:
                return result

            entity = Entity(name=name, type=type, qid=qid)
            db.add(entity)
        return entity