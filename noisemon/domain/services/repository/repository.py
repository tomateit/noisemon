from abc import ABCMeta, abstractmethod

from noisemon.domain.models.document import DocumentData, PersistedDocumentData
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import MentionData, PersistedMentionData
from noisemon.domain.models.qid import EntityQID


class Repository(metaclass=ABCMeta):
    @abstractmethod
    def get_entity_by_qid(self, qid: EntityQID) -> EntityData | None:
        ...

    @abstractmethod
    def get_entity_aliases_by_qid(self, qid: EntityQID) -> list[str]:
        ...

    @abstractmethod
    def get_mention_by_id(self, mention_id: str) -> PersistedMentionData | None:
        ...

    @abstractmethod
    def get_document_by_id(self, document_id: str) -> PersistedDocumentData | None:
        ...

    @abstractmethod
    def get_mentions_by_document_id(self, document_id: str) -> list[PersistedMentionData]:
        ...

    @abstractmethod
    def get_similar_mentions(self, mention: MentionData, max_mentions: int = 20) -> list[PersistedMentionData]:
        ...


    @abstractmethod
    def persist_new_document(self, document: DocumentData) -> PersistedDocumentData:
        ...

    @abstractmethod
    def persist_new_mention(self, mention: MentionData, document: PersistedDocumentData) -> PersistedMentionData:
        ...