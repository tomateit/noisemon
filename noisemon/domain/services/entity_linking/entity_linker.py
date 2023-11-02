from abc import ABCMeta

from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import MentionData


class EntityLinker(metaclass=ABCMeta):
    def link_entities(self, recognized_entities: list[MentionData], document: DocumentData) -> list[EntityData | None]:
        ...




