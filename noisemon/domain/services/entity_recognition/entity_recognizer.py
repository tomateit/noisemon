from abc import ABCMeta

from noisemon.domain.models.entity_span import EntitySpan

class EntityRecognizer(metaclass=ABCMeta):
    def recognize_entities(self, text: str) -> list[EntitySpan]:
        ...
