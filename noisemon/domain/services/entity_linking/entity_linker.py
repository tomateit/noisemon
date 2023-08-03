from abc import ABCMeta
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.entity_span import EntitySpan


class EntityLinker(metaclass=ABCMeta):
    def link_entities(self, text: str, recognized_entities: list[EntitySpan]) -> list[EntityData]:
        ...




