import spacy_alignments as tokenizations
import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Tuple


class ContextualEmbedding:
    def __init__(self, model_name: str = "cointegrated/LaBSE-en-ru", model=None, tokenizer=None, device=torch.device("cpu")):
        if not model:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        else:
            self.model = model
            self.tokenizer = tokenizer
        self.model.to(device)
        self.embedding = None
        self.embedding_alignment = None
        self.d = 768  # dimension

    def embed_text(self, text) -> None:
        """
        Creates an embedding, and stores it in `self.embedding` attr for further use
        """
        encoded_text = self.tokenizer([text], truncation=True, max_length=512, return_tensors="pt")
        wordpieces = self.tokenizer.batch_decode(encoded_text.input_ids[0])
        embedding_alignment, _ = tokenizations.get_alignments(list(text), wordpieces)
        self.embedding_alignment = embedding_alignment
        with torch.no_grad():
            model_output = self.model(**{k: v.to(self.model.device) for k, v in encoded_text.items()})
        embeddings = model_output.last_hidden_state.cpu()
        self.embedding = torch.nn.functional.normalize(embeddings).squeeze()

    def get_char_span_vectors(self, char_spans: List[Tuple[int, int]], preserve_embedding: bool = False) -> List[torch.Tensor]:
        """
        Given a list of char spans, returst matching embedding vectors of previously embedded text.
        If preserve_embedding is false, the precalculated embeddings will be removed
        """
        assert self.embedding is not None, "Please, run `embed_text` at first. I have to store an embedding internally"
        span_vectors = []
        for span in char_spans:
            span_idxs = [idx for list_of_indices in self.embedding_alignment[span[0]: span[1]] for idx in
                         list_of_indices]
            span_idxs = sorted(set(span_idxs))
            span_emb = self.embedding[span_idxs]
            span_vector = torch.mean(span_emb, dim=0)
            span_vectors.append(span_vector)

        if not preserve_embedding:
            self.embedding = None
            self.embedding_alignment = None

        return span_vectors
