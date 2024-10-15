from abc import abstractmethod, ABC
from typing import Generator

from noisemon.domain.models.document import DocumentData


class Consumer(ABC):
    @abstractmethod
    def get_new_document(self) -> Generator[DocumentData, None, None]: ...

    @abstractmethod
    def ack_last_document(self): ...

    @abstractmethod
    def nack_last_document(self): ...

    @abstractmethod
    def graceful_shutdown(self): ...
