import spacy_alignments as tokenizations
import torch
from transformers import AutoTokenizer, AutoModel, RobertaTokenizerFast

from noisemon.domain.models.entity_span import EntitySpanData
from noisemon.domain.services.language_representation.contextual_embedder import (
    ContextualEmbedder,
)


class ContextualEmbedderLocalImpl(ContextualEmbedder):
    model_name = "intfloat/multilingual-e5-large"

    def __init__(
        self,
        model_name=None,
        model=None,
        tokenizer=None,
        device=None,
    ):
        if device is None:
            device = torch.device("cpu")

        if model_name is not None:
            self.model_name = model_name

        if model is None:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModel.from_pretrained(self.model_name)

        self.model = model
        self.tokenizer: RobertaTokenizerFast = tokenizer
        self.model.to(device)

    def vectorize_text(self, text: str):
        assert type(text) is str, type(text)
        max_length = 512
        stride = 256

        # Tokenize the text to check its length
        tokens = self.tokenizer(text, add_special_tokens=False).input_ids

        if len(tokens) <= max_length:
            # If the text fits within the max token limit, encode normally
            encoded_text = self.tokenizer(
                [text],
                truncation=False,
                max_length=max_length,
                return_tensors="pt",
                add_special_tokens=False,
            )
            with torch.no_grad():
                model_output = self.model(
                    **{k: v.to(self.model.device) for k, v in encoded_text.items()}
                )
            embeddings = model_output.last_hidden_state.cpu().squeeze(0)  # (seq_len, hidden_size)
        else:
            # If the text is too long, use overlapping chunks
            all_embeddings = []
            for start in range(0, len(tokens), stride):
                end = min(start + max_length, len(tokens))
                token_chunk = tokens[start:end]
                encoded_chunk = self.tokenizer(
                    [self.tokenizer.decode(token_chunk)],
                    truncation=False,
                    max_length=max_length,
                    return_tensors="pt",
                    add_special_tokens=False,
                )

                with torch.no_grad():
                    model_output = self.model(
                        **{k: v.to(self.model.device) for k, v in encoded_chunk.items()}
                    )

                embeddings = model_output.last_hidden_state.cpu().squeeze(0)  # (seq_len, hidden_size)
                all_embeddings.append((start, embeddings))

            # Combine the overlapping embeddings with averaging in the overlap region
            combined_embeddings = []
            for i, (start, embedding) in enumerate(all_embeddings):
                if i == 0:
                    combined_embeddings = embedding
                else:
                    overlap_start = len(combined_embeddings) - stride
                    non_overlap_part = embedding[stride:]
                    overlap_part_left = combined_embeddings[overlap_start:]
                    overlap_part_right = embedding[:stride]

                    # Calculate the mean for the overlapping part
                    overlap_part = (overlap_part_left + overlap_part_right) / 2

                    # Concatenate the averaged overlap with the non-overlapping part
                    combined_embeddings = torch.cat((combined_embeddings[:overlap_start], overlap_part, non_overlap_part), dim=0)
            embeddings = combined_embeddings

        assert embeddings.size(0) == len(tokens), f"The size of the embeddings {embeddings.size(0)} does not match the number of tokens {len(tokens)}."
        return embeddings, tokens

    def get_char_span_vectors(
        self, text: str, char_spans: list[EntitySpanData],
    ) -> list[torch.Tensor]:
        embeddings, tokens = self.vectorize_text(text)
        wordpieces = self.tokenizer.batch_decode(tokens)
        embedding_alignment, _ = tokenizations.get_alignments(list(text), wordpieces)

        span_vectors = []
        for span in char_spans:
            span_idxs = [
                idx
                for list_of_indices in embedding_alignment[
                    span.span_start : span.span_end
                ]
                for idx in list_of_indices
            ]
            span_idxs = sorted(set(span_idxs))
            span_emb = embeddings[span_idxs]  # (x, hidden_size)
            span_vector = torch.mean(span_emb, dim=0)  # [hidden_size]
            # span_vector = torch.nn.functional.normalize(span_vector, dim=0)
            span_vectors.append(span_vector)

        return span_vectors

    def get_char_span_vector_from_long_text(
        self, text: str, char_spans: list[EntitySpanData],
    ) -> list[torch.Tensor]:
        return self.get_char_span_vectors(text, char_spans)



class ContextualEmbedderLocalImplOld(ContextualEmbedder):
    model_name = "intfloat/multilingual-e5-large"

    def __init__(
        self,
        model_name=None,
        model=None,
        tokenizer=None,
        device=None,
    ):
        if device is None:
            device = torch.device("cpu")

        if model_name is not None:
            self.model_name = model_name

        if model is None:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModel.from_pretrained(self.model_name)

        self.model = model
        self.tokenizer: RobertaTokenizerFast = tokenizer
        self.model.to(device)

    def get_char_span_vectors(
        self, text: str, char_spans: list[EntitySpanData],
    ) -> list[torch.Tensor]:
        assert type(text) is str, type(text)
        encoded_text = self.tokenizer(
            [text], truncation=True, max_length=512, return_tensors="pt",
        )
        wordpieces = self.tokenizer.batch_decode(encoded_text.input_ids[0])

        embedding_alignment, _ = tokenizations.get_alignments(list(text), wordpieces)

        with torch.no_grad():
            model_output = self.model(
                **{k: v.to(self.model.device) for k, v in encoded_text.items()}
            )

        embeddings = model_output.last_hidden_state.cpu()  # (1, 512, 1024)
        embedding = embeddings.squeeze()  # (512, 1024)

        span_vectors = []
        for span in char_spans:
            span_idxs = [
                idx
                for list_of_indices in embedding_alignment[
                    span.span_start : span.span_end
                ]
                for idx in list_of_indices
            ]
            span_idxs = sorted(set(span_idxs))
            span_emb = embedding[span_idxs]  # (x, 1024)
            span_vector = torch.mean(span_emb, dim=0)  # [1024]
            # span_vector = torch.nn.functional.normalize(span_vector, dim=0)
            span_vectors.append(span_vector)

        return span_vectors

    def get_char_span_vector_from_long_text(
        self, text: str, char_spans: list[EntitySpanData],
    ) -> list[torch.Tensor]:
        assert type(text) is str, type(text)
        stride = 256  # Overlapping stride to ensure coverage without truncation
        max_length = 512

        # Tokenize the text to get tokens for chunking
        tokens = self.tokenizer(text, add_special_tokens=False).input_ids

        # Break the tokens into overlapping chunks and store their embeddings
        all_embeddings = []
        for start in range(0, len(tokens), stride):
            end = min(start + max_length, len(tokens))
            token_chunk = tokens[start:end]
            encoded_chunk = self.tokenizer(
                [self.tokenizer.decode(token_chunk)], truncation=True, max_length=max_length, return_tensors="pt",
            )

            with torch.no_grad():
                model_output = self.model(
                    **{k: v.to(self.model.device) for k, v in encoded_chunk.items()}
                )

            embeddings = model_output.last_hidden_state.cpu()  # (1, seq_len, hidden_size)
            embedding = embeddings.squeeze(0)  # (seq_len, hidden_size)
            all_embeddings.append((start, embedding))

        # Combine the overlapping embeddings with averaging in the overlap region
        combined_embeddings = []
        for i, (start, embedding) in enumerate(all_embeddings):
            if i == 0:
                combined_embeddings = embedding
            else:
                overlap_start = len(combined_embeddings) - stride
                non_overlap_part = embedding[stride:]
                overlap_part_left = combined_embeddings[overlap_start:]
                overlap_part_right = embedding[:stride]

                # Calculate the mean for the overlapping part
                overlap_part = (overlap_part_left + overlap_part_right) / 2

                # Concatenate the averaged overlap with the non-overlapping part
                combined_embeddings = torch.cat((combined_embeddings[:overlap_start], overlap_part, non_overlap_part), dim=0)

        # Extract span vectors from the combined embeddings
        wordpieces = self.tokenizer.batch_decode(tokens)
        embedding_alignment, _ = tokenizations.get_alignments(list(text), wordpieces)

        span_vectors = []
        for span in char_spans:
            span_idxs = [
                idx
                for list_of_indices in embedding_alignment[
                    span.span_start : span.span_end
                ]
                for idx in list_of_indices
            ]
            span_idxs = sorted(set(span_idxs))
            span_emb = combined_embeddings[span_idxs]  # (x, hidden_size)
            span_vector = torch.mean(span_emb, dim=0)  # [hidden_size]
            # span_vector = torch.nn.functional.normalize(span_vector, dim=0)
            span_vectors.append(span_vector)

        return span_vectors
