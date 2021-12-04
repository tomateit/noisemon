"""
One and only module that opetares with faiss index and performs vector search
"""
import json
import logging
from typing import List, Dict, Tuple, Union, Optional, Iterable
from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter
from pprint import pprint

import torch
import numpy as np
from spacy.tokens import Doc, Span

# import crud
from vector_index import VectorIndex
from models import Entity, VectorIndexModel
from database import SessionLocal, engine
from tools.span_to_vector import span_to_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EntityLinker:
    def __init__(
        self,
        k_neighbors: int = 4,
        cutoff_threshold: float = 0.8,
    ):
        # self.d = self.embedder.d  # dimension
        self.d = 768
        self.db = SessionLocal()
        self.vector_index = VectorIndex(self.d)
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        logging.debug("EntityLinker initialized")


    def link_entities(self, doc: Doc) -> List[Union[Entity, None]]:
        """
        Links provided doc ents with known entities and returns a list of `Entity` models.
        If a span does not resemple any of QID aliases, will return `None`, otherwise `Entity`.
        Doc must contain ._.trf_data to get span embeddings
        The resulting list is of the same length as doc.ents
        """
        linked_entities: List[Union[Entity, None]] = [] # Entities that were matched to QID
        recognized_entities: List[Span] = [ent for ent in doc.ents if ent.label_ == "ORG"] # All detected entities of type
        print(recognized_entities)
        # recognized_entities = [text[e[0] : e[1]] for e in spans]

        # 1. ENTITY VECTORS LOOKUP
        entity_vectors_list: List[np.ndarray] = [span_to_vector(doc, ent.start, ent.end) for ent in recognized_entities]
        tensor_of_entities: np.ndarray = np.vstack(entity_vectors_list).astype(np.float32)
        logger.debug(f"For provided entity spans, got following embeding matrix: {tensor_of_entities.shape}")

        # index search shall be in one operation cuz fast
        I: List[List[int]] = self.vector_index.find_closes_indices_batch(tensor_of_entities, self.k_neighbors)
        # I is (len(spans), k)

        # 2. ENTITY CANDIDATES LOOKUP
        # TODO switch to flatmap
        list_of_candidate_lists: List[List[Union[VectorIndexModel, None]]] = []
        for candidates_for_span in I:
            buffer: List[Optional[VectorIndexModel]] = []
            for candidate_index in candidates_for_span:
                candidate = None
                if candidate_index != -1:
                    candidate: Optional[VectorIndexModel] = self.vector_index.get_vector_model_by_index(candidate_index)
                buffer.append(candidate)
            list_of_candidate_lists.append(buffer)
        pprint(list_of_candidate_lists)

        # 3. Strategy: choosing majority
        for candidate_list, recognized_entity, entity_vector in zip(list_of_candidate_lists, recognized_entities, entity_vectors_list):
            if not any(candidate_list): # all candidates may be none, we ask for at least one
                linked_entities.append(None)
                continue

            vector_index, count = self.get_majority_by(candidate_list, "entity_qid")
            major_entity: Entity = vector_index.entity # even if each entity appears 1 time this will be leftmost thus closest

            # We can not just return any QID we got from vector query.
            # If the entity is completely unknown there still will be a result
            # Thus check span to be alike one of QID aliases
            if self.similarity(recognized_entity.text, major_entity.aliases) < self.cutoff_threshold:
                linked_entities.append(None)
            else:
                # 1. Increment number of matches for a vector
                self.vector_index.increment_number_of_mentions(vector_index)
                linked_entities.append(major_entity)
                logger.debug(f"Vector recognized for entity {major_entity.qid}")
                # 2. Create new vector for the recognized entity
                vector = entity_vector.reshape((1, self.d)).astype(np.float32)
                self.vector_index.add_entity_vector(entity=major_entity, vector=vector, span=recognized_entity.text, source="overpopulation")
                logger.debug(f"New vector created for span {recognized_entity} as {major_entity.qid}")

            
        return linked_entities


    def get_majority_by(self, candidates: List, field: str):
        """
        Returns the leftmost candidate with most frequent field value and its respective count (Nones ignored)
        """
        qids = [getattr(c, field) for c in candidates if c is not None]
        QID, count = Counter(qids).most_common(1)[0]
        for c in candidates:
            if c is not None  and getattr(c, field) == QID:
                return c, count
        raise Exception("WTF")


    def similarity(self, A: str, Bs: Iterable[str]) -> float:
        """
        Calculates similarity between A and each of B, returns maximum
        """
        A = A.lower()
        return max([SequenceMatcher(None, A, B.lower()).ratio() for B in Bs])
