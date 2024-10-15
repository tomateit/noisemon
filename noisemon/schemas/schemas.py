"""
Schemas file is used for external contract and data shape specification
For application-wide models use noisemon.models
"""

from dataclasses import dataclass
from enum import Enum
import uuid
import datetime


class ResourceTypes(str, Enum):
    dataset = "dataset"
    website = "website"
    telegram_channel = "telegram_channel"

@dataclass(frozen=True)
class ResourceSchema:
    resource_id: uuid.UUID
    resource_type: ResourceTypes
    resource_name: str
    uri: str
    created_at: datetime.datetime

@dataclass(frozen=True)
class ResourceLinkSchema:
    resource_id: uuid.UUID
    name: str
    uri: str | None


@dataclass(frozen=True)
class MentionSchema:
    span_start: int
    span_end: int
    span: str
    entity_qid: str | None

@dataclass(frozen=True)
class DocumentSchema:
    original_text: str

@dataclass(frozen=True)
class DatasetRowSchema:
    resource_link: ResourceLinkSchema
    document: DocumentSchema
    mentions: MentionSchema

@dataclass(frozen=True)
class DatasetSchema:
    resource: ResourceSchema
    entries: list[DatasetRowSchema]