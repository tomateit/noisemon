import datetime
import uuid

import sqlalchemy
import uuid_utils
from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped
from pgvector.sqlalchemy import Vector

from noisemon.domain.models.document import DocumentData, PersistedDocumentData

# from noisemon.domain.models.document_origin import DocumentOrigin
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import PersistedMentionData
from noisemon.domain.models.qid import EntityQID
from noisemon.domain.models.resource import ResourceTypes, ResourceData


class Base(DeclarativeBase): ...


def generate_uuid():
    return uuid.UUID(str(uuid_utils.uuid7()))


def generate_timestamp():
    return datetime.datetime.now(tz=datetime.UTC)


class DocumentModel(Base):
    __tablename__ = "documents"
    document_id: Mapped[uuid.UUID] = Column(
        PostgresUUID(as_uuid=True),
        name="document_id",
        primary_key=True,
        default=generate_uuid,
    )

    # signify stages of source content processing, from the rawest possible (why not bytes?) to the most processed
    raw_content: Mapped[str | None] = Column(TEXT, nullable=True)
    content: Mapped[str | None] = Column(TEXT, nullable=True)
    raw_text: Mapped[str | None] = Column(TEXT, nullable=True)
    text: Mapped[str | None] = Column(TEXT, nullable=True)

    mentions = relationship(
        "MentionModel", back_populates="document", cascade="all,delete"
    )


class MentionModel(Base):
    __tablename__ = "mentions"
    mention_id: Mapped[uuid.UUID] = Column(
        PostgresUUID(as_uuid=True),
        name="mention_id",
        primary_key=True,
        default=generate_uuid,
    )
    document_id: Mapped[uuid.UUID] = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("documents.document_id"),
        name="document_id",
        nullable=False,
    )
    entity_qid: Mapped[str] = Column(
        TEXT, ForeignKey("entities.entity_qid"), name="entity_qid", nullable=True
    )

    span: Mapped[str] = Column(TEXT, name="span", nullable=False)  # textual form
    span_start: Mapped[int] = Column(TEXT, name="span_start", nullable=False)
    span_end: Mapped[int] = Column(TEXT, name="span_end", nullable=False)

    vector = Column(Vector, name="vector", nullable=True)  # (d,)

    entity = relationship("EntityModel", back_populates="mentions")
    document = relationship("DocumentModel", back_populates="mentions")

    def __repr__(self):
        return f"Mention[span={self.span},qid={self.entity_qid}]"


class EntityModel(Base):
    __tablename__ = "entities"
    entity_qid: Mapped[str] = Column(TEXT, name="entity_qid", primary_key=True)
    label: Mapped[str | None] = Column(TEXT, unique=False, nullable=True)
    description: Mapped[str | None] = Column(TEXT, unique=False, nullable=True)

    mentions = relationship("MentionModel", back_populates="entity")

    def __repr__(self):
        return f"EntityModel[qid={self.entity_qid}]"

    # @property
    # def aliases(self) -> set[str]:
    #     return set([x.span for x in self.mentions])


class ResourceLinkORMModel(Base):
    __tablename__ = "resource_links"
    resource_link_id: Mapped[uuid.UUID] = Column(
        PostgresUUID(as_uuid=True),
        name="mention_id",
        primary_key=True,
        default=generate_uuid,
    )
    resource_id: Mapped[uuid.UUID] = Column(
        PostgresUUID(as_uuid=True), name="resource_id", nullable=False
    )
    name: Mapped[str] = Column(TEXT, unique=False, nullable=True)
    uri: Mapped[str] = Column(TEXT, unique=True, nullable=True)


class ResourceModel(Base):
    __tablename__ = "resources"
    resource_id: Mapped[uuid.UUID] = Column(
        PostgresUUID(as_uuid=True),
        name="resource_id",
        primary_key=True,
        default=generate_uuid,
    )
    resource_name: Mapped[str] = Column(TEXT, unique=False, nullable=True)
    resource_type: Mapped[ResourceTypes] = Column(
        sqlalchemy.Enum(ResourceTypes), unique=False, nullable=False
    )
    uri: Mapped[str] = Column(TEXT, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = Column(
        TIMESTAMP(timezone=True), default=generate_timestamp
    )


def resource_dataclass_to_model(o) -> ResourceModel:
    return ResourceModel(
        resource_id=o.resource_id,
        resource_name=o.resource_name,
        resource_type=o.resource_type,
        uri=str(o.uri),
        created_at=o.created_at,
    )


def resource_model_to_dataclass(o) -> ResourceData:
    return ResourceData(
        resource_id=o.resource_id,
        resource_name=o.resource_name,
        resource_type=o.resource_type,
        uri=o.uri,
        created_at=o.created_at,
    )


def entity_model_to_dataclass(o) -> EntityData:
    return EntityData(
        entity_qid=EntityQID(o.entity_qid),
        label=o.label,
        description=o.description,
    )


def entity_dataclass_to_model(o: EntityData) -> EntityModel:
    return EntityModel(
        entity_qid=str(o.entity_qid),
        label=o.label,
        description=o.description,
    )


def document_model_to_dataclass(o) -> PersistedDocumentData:
    return PersistedDocumentData(
        document_id=o.document_id,
        text=o.text,
        raw_text=o.raw_text,
        content=o.content,
        raw_content=o.raw_content,
    )


def document_dataclass_to_model(o: DocumentData) -> DocumentModel:
    return DocumentModel(
        text=o.text,
        raw_text=o.raw_text,
        document_id=o.document_id,
    )


def entity_dataclass_to_dict(o: EntityData) -> dict:
    return dict(
        entity_qid=str(o.entity_qid),
    )


def entity_model_to_dict(o: EntityModel) -> dict:
    return dict(
        entity_qid=o.entity_qid,
    )


def mention_model_to_dataclass(o) -> PersistedMentionData:
    return PersistedMentionData(
        span=o.span,
        span_start=o.span_start,
        span_end=o.span_end,
        document_id=o.document_id,
        mention_id=o.mention_id,
        entity_qid=EntityQID(o.entity_qid),
        vector=o.vector,
    )


def mention_dataclass_to_model(o) -> MentionModel:
    return MentionModel(
        span=o.span,
        span_start=o.span_start,
        span_end=o.span_end,
        document_id=o.document_id,
        mention_id=o.mention_id,
        entity_qid=str(o.entity_qid),
        vector=o.vector,
    )
