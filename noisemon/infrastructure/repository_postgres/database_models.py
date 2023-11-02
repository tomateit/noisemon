import uuid
from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TEXT, TIMESTAMP, INTEGER
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

from noisemon.domain.models.document import DocumentData, PersistedDocumentData
# from noisemon.domain.models.document_origin import DocumentOrigin
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import PersistedMentionData
from noisemon.domain.models.qid import EntityQID


Base = declarative_base()
def generate_uuid():
    return str(uuid.uuid4())

class DocumentModel(Base):
    __tablename__ = "documents"
    document_id = Column(TEXT, name="document_id", primary_key=True, default=generate_uuid)
    # origin = Column(JSONB, name="origin")

    raw_content = Column(TEXT, nullable=True)
    content = Column(TEXT, nullable=True)
    raw_text = Column(TEXT, nullable=True)
    text = Column(TEXT, nullable=True)

    mentions = relationship("MentionModel", back_populates="document", cascade="all,delete")



class MentionModel(Base):
    __tablename__ = "mentions"
    mention_id = Column(TEXT, name="mention_id", primary_key=True, default=generate_uuid)
    document_id = Column(TEXT, ForeignKey("documents.document_id"), name="document_id", nullable=False)
    entity_qid = Column(TEXT, ForeignKey("entities.entity_qid"), name="entity_qid", nullable=True)


    span = Column(TEXT, name="span", nullable=False)  # textual form
    span_start = Column(TEXT, name="span_start", nullable=False)
    span_end = Column(TEXT, name="span_end", nullable=False)

    vector = Column(Vector, name="vector", nullable=True)  # (d,) vector as bytes "float32"


    entity = relationship("EntityModel", back_populates="mentions")
    document = relationship("DocumentModel", back_populates="mentions")
    def __repr__(self):
        return f"Mention[span={self.span},qid={self.entity_qid}]"


class EntityModel(Base):
    __tablename__ = "entities"
    entity_qid = Column(TEXT, name="entity_qid", primary_key=True)
    # name = Column(TEXT, unique=False, nullable=True)

    mentions = relationship("MentionModel", back_populates="entity")

    # def __repr__(self):
    #     return f"EntityModel[name={self.name},qid={self.qid}]"

    def __repr__(self):
        return f"EntityModel[qid={self.qid}]"

    @property
    def aliases(self) -> set[str]:
        return set([x.span for x in self.mentions])


def entity_dataclass_to_model(o: EntityData) -> EntityModel:
    return EntityModel(
        entity_qid=o.entity_qid,
        # name=o.name,
    )


def document_model_to_dataclass(o) -> PersistedDocumentData:
    return PersistedDocumentData(
        # origin=DocumentOrigin(**o.origin),
        document_id=o.document_id,
        text=o.text,
        raw_text=o.raw_text,
        content=o.content,
        raw_content=o.raw_content
    )


def document_dataclass_to_model(o: DocumentData) -> DocumentModel:
    return DocumentModel(
        # origin=asdict(o.origin),
        text=o.text,
        raw_text=o.raw_text,
        document_id=o.document_id,
    )


def entity_dataclass_to_dict(o: EntityData) -> dict:
    return dict(
        entity_qid=o.entity_qid,
        # name=o.name,
    )


def entity_model_to_dict(o: EntityModel) -> dict:
    return dict(
        qid=o.qid,
        name=o.name,
        type=o.type
    )

def entity_model_to_dataclass(o: EntityModel) -> EntityData:
    return EntityData(
        entity_qid=o.entity_qid,
    )

def mention_model_to_dataclass(o) -> PersistedMentionData:
    return PersistedMentionData(
        span=o.span,
        span_start=o.span_start,
        span_end=o.span_end,
        document_id=o.document_id,
        mention_id=o.mention_id,
        entity_qid=o.entity_qid,
        vector=o.vector,
    )

def mention_dataclass_to_model(o) -> MentionModel:
    return MentionModel(
        span=o.span,
        span_start=o.span_start,
        span_end=o.span_end,
        document_id=o.document_id,
        mention_id=o.mention_id,
        entity_qid=o.entity_qid,
        vector=o.vector,
    )
