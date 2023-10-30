from abc import ABCMeta, abstractmethod

from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import MentionData
from noisemon.domain.models.qid import EntityQID


class Repository(metaclass=ABCMeta):
    @abstractmethod
    def get_entity_by_qid(self, qid: EntityQID) -> EntityData | None:
        ...

    @abstractmethod
    def get_mention_by_id(self, mention_id: str) -> MentionData | None:
        ...

    @abstractmethod
    def get_document_by_id(self, document_id: str) -> DocumentData | None:
        ...
    @abstractmethod
    def get_mentions_by_document_id(self, document_id: str) -> list[MentionData]:
        ...