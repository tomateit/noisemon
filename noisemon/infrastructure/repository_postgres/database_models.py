import uuid
from dataclasses import asdict
from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TEXT, TIMESTAMP, INTEGER
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.document_origin import DocumentOrigin
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.qid import EntityQID

Base = declarative_base()
def generate_uuid():
    return str(uuid.uuid4())

class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(TEXT, name="id", primary_key=True, default=generate_uuid)
    origin = Column(JSONB, name="origin")

    text = Column(TEXT, nullable=False)
    raw_text = Column(TEXT, nullable=False)

    mentions = relationship("MentionModel", back_populates="origin")


def document_model_to_dataclass(o: DocumentModel) -> DocumentData:
    return DocumentData(
        id=o.id,
        origin=DocumentOrigin(**o.origin),
        text=o.text,
        raw_text=o.raw_text,
    )

def document_dataclass_to_model(o: DocumentData):
    return DocumentModel(
        origin=asdict(o.origin),
        text=o.text,
        raw_text=o.raw_text,
    )

class MentionModel(Base):
    __tablename__ = "mentions"
    mention_id = Column(TEXT, name="id", primary_key=True, default=generate_uuid)
    entity_qid = Column(TEXT, ForeignKey("entities.qid"), name="entity_qid", nullable=False)
    origin_id = Column(TEXT, ForeignKey("documents.id"), name="origin_id", nullable=False)



    span = Column(TEXT, name="span", nullable=False)  # textual form
    span_start = Column(TEXT, name="span_start", nullable=False)
    span_end = Column(TEXT, name="span_end", nullable=False)

    vector = Column(Vector, name="vector", nullable=True)  # (d,) vector as bytes "float32"
    # metadata for analytics
    creation_timestamp = Column(TIMESTAMP, default=datetime.now, nullable=True)

    entity = relationship("EntityModel", back_populates="mentions")
    origin = relationship("DocumentModel", back_populates="mentions")
    def __repr__(self):
        return f"Mention[span={self.span},qid={self.entity_qid}]"

class EntityModel(Base):
    __tablename__ = "entities"
    qid = Column(EntityQID, name="qid", primary_key=True)
    name = Column(TEXT, unique=False, nullable=False)

    mentions = relationship("MentionModel", back_populates="entity", cascade="all,delete")

    def __repr__(self):
        return f"EntityModel[name={self.name},qid={self.qid}]"

    @property
    def aliases(self) -> set[str]:
        return set([x.span for x in self.mentions])


def entity_dataclass_to_model(o: EntityData) -> EntityModel:
    return EntityModel(
        qid=o.qid,
        name=o.name,
    )




def entity_dataclass_to_dict(o: EntityData) -> dict:
    return dict(
        qid=o.qid,
        name=o.name,
        type=o.type
    )

def entity_model_to_dict(o: EntityModel) -> dict:
    return dict(
        qid=o.qid,
        name=o.name,
        type=o.type
    )
#