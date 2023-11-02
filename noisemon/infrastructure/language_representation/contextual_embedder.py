import spacy_alignments as tokenizations
import torch
from transformers import AutoTokenizer, AutoModel

from noisemon.domain.models.entity_span import EntitySpan
from noisemon.domain.services.language_representation.contextual_embedder import ContextualEmbedder


class ContextualEmbedderLocalImpl(ContextualEmbedder):
    model_name = "BAAI/bge-large-en-v1.5"
    def __init__(
            self,
            model_name=None,
            model=None,
            tokenizer=None,
            device=torch.device("cpu")
    ):
        if model_name is not None:
            self.model_name = model_name

        if model is None:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModel.from_pretrained(self.model_name)

        self.model = model
        self.tokenizer = tokenizer
        self.model.to(device)



    def get_char_span_vectors(self, text: str, char_spans: list[EntitySpan]) -> list[torch.Tensor]:
        encoded_text = self.tokenizer([text], truncation=True, max_length=512, return_tensors="pt")
        wordpieces = self.tokenizer.batch_decode(encoded_text.input_ids[0])

        embedding_alignment, _ = tokenizations.get_alignments(list(text), wordpieces)

        with torch.no_grad():
            model_output = self.model(**{k: v.to(self.model.device) for k, v in encoded_text.items()})

        embeddings = model_output.last_hidden_state.cpu()
        embedding = torch.nn.functional.normalize(embeddings).squeeze()

        span_vectors = []
        for span in char_spans:
            span_idxs = [idx
                         for list_of_indices in embedding_alignment[span.span_start: span.span_end]
                         for idx in list_of_indices]
            span_idxs = sorted(set(span_idxs))
            span_emb = embedding[span_idxs]
            span_vector = torch.mean(span_emb, dim=0)
            span_vectors.append(span_vector)

        return span_vectors
