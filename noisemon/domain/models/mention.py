import uuid
from dataclasses import dataclass

from noisemon.domain.models.entity_span import EntitySpanData
from noisemon.domain.models.qid import EntityQID


@dataclass(kw_only=True)
class MentionData(EntitySpanData):
    span: str
    span_start: int
    span_end: int

    document_id: uuid.UUID | None = None
    mention_id: uuid.UUID | None = None
    entity_qid: EntityQID | None = None

    vector: list[float] | None = None

@dataclass(kw_only=True)
class LinkedMentionData(MentionData):
    entity_qid: EntityQID


@dataclass(kw_only=True)
class GroundedLinkedMentionData(LinkedMentionData):
    document_id: uuid.UUID


@dataclass(kw_only=True)
class PersistedMentionData(GroundedLinkedMentionData):
    mention_id: uuid.UUID
