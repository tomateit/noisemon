from abc import ABCMeta, abstractmethod

from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.mention import MentionData


class Processor(metaclass=ABCMeta):
    @abstractmethod
    def process_document(self, document: DocumentData) -> list[MentionData]: ...
