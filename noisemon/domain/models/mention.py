from dataclasses import dataclass

from noisemon.domain.models.entity_span import EntitySpan
from noisemon.domain.models.qid import EntityQID


@dataclass(kw_only=True)
class MentionData(EntitySpan):
    span: str
    span_start: str
    span_end: str

    document_id: str | None = None
    mention_id: str | None = None
    entity_qid: EntityQID | None = None

    vector: list[float] | None = None

@dataclass(kw_only=True)
class PersistedMentionData(MentionData):
    document_id: str
    mention_id: str
