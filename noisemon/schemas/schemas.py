"""
Schemas file is used for external contract and data shape specification
For application-wide models use noisemon.models
"""

from pydantic import BaseModel
from enum import Enum
import uuid
import datetime

from noisemon.domain.models.document import PersistedDocumentData, DocumentData
from noisemon.domain.models.mention import MentionData, GroundedLinkedMentionData, LinkedMentionData
from noisemon.domain.models.qid import EntityQID
from noisemon.domain.models.resource import ResourceData
from noisemon.domain.models.resource_link import ResourceLinkData, PersistedResourceLinkData


class ResourceTypes(str, Enum):
    dataset = "dataset"
    website = "website"
    telegram_channel = "telegram_channel"


class ResourceSchema(BaseModel):
    resource_id: uuid.UUID
    resource_type: ResourceTypes
    resource_name: str
    uri: str
    created_at: datetime.datetime

    def to_domain_model(self):
        return ResourceData(
            resource_id=self.resource_id,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            uri=self.uri,
            created_at=self.created_at,
        )


class ResourceLinkSchema(BaseModel):
    """INDIVIDUAL PER DOCUMENT"""
    resource_id: uuid.UUID
    name: str
    uri: str | None
    publication_timestamp: datetime.datetime

    def to_domain_model(self):
        return ResourceLinkData(
            resource_id=self.resource_id,
            name=self.name,
            uri=self.uri,
            publication_timestamp=self.publication_timestamp,
        )

class MentionSchema(BaseModel):
    span_start: int
    span_end: int
    span: str
    entity_qid: str

    def to_domain_model(self):
        entity_qid = EntityQID(self.entity_qid)
        return LinkedMentionData(
            span_start=self.span_start,
            span_end=self.span_end,
            span=self.span,
            entity_qid=entity_qid,
        )


class DocumentSchema(BaseModel):
    original_text: str

    def to_domain_model(self):
        return DocumentData(
            raw_text=self.original_text,
        )


class DatasetRowSchema(BaseModel):
    resource_link: ResourceLinkSchema
    document: DocumentSchema
    mentions: list[MentionSchema]

class DatasetSchema(BaseModel):
    resource: ResourceSchema
    entries: list[DatasetRowSchema]