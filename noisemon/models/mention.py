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


class Mention(Base):
    __tablename__ = "mentions"
    mention_id = Column(String, name="id", primary_key=True, default=generate_uuid)
    source = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    entity_qid = Column(String, ForeignKey("entities.qid"), nullable=False)

    entity = relationship("Entity", back_populates="mentions")

    @staticmethod
    def create_entity_mention(db: Session, entity: Entity, timestamp: str, source: str):
        with db.begin():
            mention = Mention(
                entity_qid=entity.qid, 
                timestamp=datetime.fromisoformat(timestamp), 
                source=source
            )
            db.add(mention)
        return mention