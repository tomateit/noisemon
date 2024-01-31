from abc import abstractmethod, ABC

from noisemon.domain.models.document import DocumentData


class Consumer(ABC):

    @abstractmethod
    def get_new_document(self) -> DocumentData:
        ...
