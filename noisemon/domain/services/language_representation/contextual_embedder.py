import torch

from noisemon.domain.models.entity_span import EntitySpanData
from abc import abstractmethod, ABCMeta


class ContextualEmbedder(metaclass=ABCMeta):
    @abstractmethod
    def get_char_span_vectors(
        self, text: str, char_spans: list[EntitySpanData]
    ) -> list[torch.Tensor]: ...
