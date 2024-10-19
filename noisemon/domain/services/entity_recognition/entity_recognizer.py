from abc import ABCMeta, abstractmethod

from noisemon.domain.models.entity_span import EntitySpanData


class EntityRecognizer(metaclass=ABCMeta):
    @abstractmethod
    def recognize_entities(self, text: str) -> list[EntitySpanData]: ...
