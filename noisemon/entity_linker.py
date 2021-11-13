"""
One and only module that opetares with faiss index and performs vector search
"""
import json
import logging
from typing import List, Dict, Tuple, Union
from pathlib import Path
from difflib import SequenceMatcher

import faiss
import torch
import numpy as np

import crud
from models import VectorIndex, Entity
from database import SessionLocal, engine
from tools.char_span_to_vector import ContextualEmbedding

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EntityLinker:
    def __init__(
        self,
        k_neighbors: int = 4,
        cutoff_threshold: float = 0.8,
    ):
        self.embedder = ContextualEmbedding()
        self.d = self.embedder.d  # dimension
        self.db = SessionLocal()
        self.build_faiss_index()
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        logging.debug("EntityLinker initialized")

    def build_faiss_index(self):
        """
        Reads out vectors from database and creates vector index. Used on class initialization only
        """
        vectors = crud.get_all_active_vectors(self.db)
        tensor = np.vstack(vectors)

        self.faiss_index = faiss.IndexFlatIP(self.d)  # build the index
        self.faiss_index.add(tensor)  # add vectors to the index

    def link_entities(
        self, text: str, spans: List[Tuple[int, int]]
    ) -> List[Union[Entity, None]]:
        """
        Links provided text spans with entities and returns a list of entity QIDs.
        If span does not resemple any of QID aliases, will return `None`, otherwise `QID`.
        The text is required to infer contextual vectors.
        """
        if not spans:
            return []
        detected_entities = []
        entity_spans = [text[e[0] : e[1]] for e in spans]
        self.embedder.embed_text(text)
        entity_vectors_list: List[torch.Tensor] = self.embedder.get_char_span_vectors(
            spans
        )
        entity_vectors: numpy.ndarray = torch.vstack(entity_vectors_list).numpy()
        logger.debug(f"For provided entity spans, got following embeding matrix: {entity_vectors.shape}")

        # index search shall be in one operation cuz fast
        D, I = self.faiss_index.search(entity_vectors, self.k_neighbors)
        # I is (len(spans), k)
        qid_candidates: List[List[Union[VectorIndex, None]]] = []
        for span_vec_idx_candidates in list(I):
            buff = [
                crud.get_vector_index_by_index(self.db, int(index))
                if int(index) != -1
                else None
                for index in span_vec_idx_candidates
            ]
            qid_candidates.append(buff)

        # Strategy: choosing majority
        for candidate_list, entity_span, entity_vector in zip(qid_candidates, entity_spans, entity_vectors_list):
            if not all(candidate_list):
                detected_entities.append(None)
                continue

            vector_index, count = VectorIndex.get_major(candidate_list)
            entity = vector_index.entity

            if count == 1:
                # to ensure that we choose the closest vector, I choose the first candidate
                # bc they are already sorted by cosine distance
                vector_index = candidate_list[0]
                entity = vector_index.entity
            # We can not just return any QID.
            # If the entity is completely unknown there still will be a result
            # Thus check to be alike one of QID aliases
            list_of_aliases = entity.aliases
            if self.similarity(entity_span, list_of_aliases) < self.cutoff_threshold:
                entity = None
            else:
                crud.increment_number_of_mentions(self.db, vector_index)
                logger.debug(f"Vector recognized for entity {entity.qid}")
                vector = entity_vector.numpy().reshape((1, self.d))
                self.add_entity_vector(
                    entity=entity, vector=vector, span=entity_span, source="overpopulation"
                )
                logger.debug(
                    f"New vector created for span {entity_span} as {entity.qid}"
                )

            detected_entities.append(entity)

        return detected_entities

    def add_entity_vector(
        self, entity: Entity, vector: np.ndarray, span: str, source="online"
    ) -> VectorIndex:
        """
        Adds a new vector into faiss, creates new VectorIndex entity, saves faiss dump
        """
        assert vector.shape == (1, self.d), f"Incompatible shape: {vector.shape}, expected {(1, self.d)}"
        # TODO Ensure the order of operations is good
        next_faiss_index = self.faiss_index.ntotal
        self.faiss_index.add(vector)
        new_vector_index = crud.create_vector_index(
            self.db,
            entity_qid=entity.qid,
            index=next_faiss_index,
            span=span,
            source=source,
            vector=vector,
        )
        logger.debug(
            f"Added vector number {next_faiss_index} for span '{span}' of entity {entity.qid}"
        )
        return new_vector_index

    def similarity(self, A: str, Bs: List[str]) -> float:
        """
        Calculates similarity between A and each of B, returns maximum
        """
        A = A.lower()
        return max([SequenceMatcher(None, A, B.lower()).ratio() for B in Bs])
