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

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, name="id", primary_key=True, default=generate_uuid)
    #  = Column(String, ForeignKey("entities.qid"), nullable=False)
    link = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    text=Column(String, nullable=False)
    raw_text = Column(String, nullable=False)

    mentions = relationship("Mention", back_populates="origin")

