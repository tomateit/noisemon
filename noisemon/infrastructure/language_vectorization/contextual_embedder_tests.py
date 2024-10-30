import torch

from noisemon.domain.models.entity_span import EntitySpanData
from noisemon.infrastructure.language_vectorization.contextual_embedder import ContextualEmbedderLocalImpl


class TestContextualEmbedderLocalImpl:
    @classmethod
    def setup_class(cls):
        cls.embedder = ContextualEmbedderLocalImpl()

    def test_short_text_embedding(self):
        text = "This is a short test sentence."
        char_spans = [
            EntitySpanData(span="short", span_start=10, span_end=15),
            EntitySpanData(span="test", span_start=16, span_end=20),
        ]
        span_vectors = self.embedder.get_char_span_vectors(text, char_spans)
        assert len(span_vectors) == len(char_spans)
        for vector in span_vectors:
            assert vector.shape == torch.Size([self.embedder.model.config.hidden_size])

    def test_long_text_embedding(self):
        text = "This is a longer text designed to test how the embedder handles texts that exceed the maximum token length allowed by the model. " * 10
        char_spans = [
            EntitySpanData(span="longer", span_start=10, span_end=16),
            EntitySpanData(span="handles", span_start=100, span_end=107),
            EntitySpanData(span="allowed", span_start=200, span_end=207),
        ]
        span_vectors = self.embedder.get_char_span_vector_from_long_text(text, char_spans)
        assert len(span_vectors) == len(char_spans)
        for vector in span_vectors:
            assert vector.shape == torch.Size([self.embedder.model.config.hidden_size])