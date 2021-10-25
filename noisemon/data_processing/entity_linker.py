"""
One and only module that opetares with faiss index and performs vector serach
"""
from typing import List, Dict, Tuple, Union
import json
from pathlib import Path
from difflib import SequenceMatcher
import faiss
import torch
import numpy as np
from scripts.char_span_to_vector import ContextualEmbedding
from collections import Counter
import logging
import crud
from database import SessionLocal, engine

class EntityLinker():
    def __init__(
        self, 
        faiss_index_path: Path,
        k_neighbors: int = 4,
        cutoff_threshold: float = 0.8,
        ):
        self.db = SessionLocal()
        self.faiss_index = faiss.read_index(str(faiss_index_path))
        self.embedder = ContextualEmbedding()
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        logging.debug("EntityLinker initialized")

    def link_entities(self, text: str, spans: List[Tuple[int, int]]) -> List[Union[str, None]]:
        """
        Links provided text spans with entities and returns a list of entity QIDs. 
        If span does not resemple any of QID aliases, will return `None`, otherwise `QID`.
        The text is required to infer contextual vectors.
        """
        if not spans:
            return []
        detected_qids = []
        entities = [text[e[0]:e[1]] for e in spans]
        self.embedder.embed_text(text)
        entity_vectors: List[torch.Tensor] = self.embedder.get_char_span_vectors(spans)
        entity_vectors: numpy.ndarray = torch.vstack(entity_vectors).numpy()
        print("For provided entity spans, got following embeding matrix: ", entity_vectors.shape)

        # index search shall be in one operation cuz fast
        D, I = self.faiss_index.search(entity_vectors, self.k_neighbors) 
        # I is (len(spans), k)
        qid_candidates: List[List[str]] = []
        for span_vec_idx_candidates in list(I):
            buff = []
            for vector_index in span_vec_idx_candidates:
                try:
                    qid_candidate = crud.get_qid_by_vector_index(self.db, int(vector_index))
                    buff.append(qid_candidate)
                except KeyError as e:
                    print("Key error")
                    print(span_vec_idx_candidates)
                    print(I)
                    print(D)
                    print(e)
                    return []
            qid_candidates.append(buff)

        # Strategy: choosing majority
        for candidate_list, entity in zip(qid_candidates, entities):
            QID, count = Counter(candidate_list).most_common(1)[0]
            if count == 1:
                # to ensure that we choose the closest vector, I choose the first candidate
                # bc they are already sorted by cosine distance
                QID = candidate_list[0]
            # We can not just return any QID.
            # If the entity is completely unknown there still will be a result
            # Thus check to be alike one of QID aliases
            list_of_aliases = crud.get_aliases_by_qid(self.db, QID)
            if not list_of_aliases or (self.similarity(entity, list_of_aliases) < self.cutoff_threshold):
                QID = None

            detected_qids.append(QID)

        return detected_qids

    def add_entity_vector(self, entity_qid: str, vector: np.ndarray, span: str) -> int:
        """
        Adds a new vector into faiss, creates new VectorIndex entity, saves faiss dump
        """
        self.faiss_index.add(vector)
        next_index = self.faiss_index.ntotal + 1
        crud.create_vector_index(self.db, entity_qid = entity_qid, index = next_index, span = span, source = "online")
        print(f"Added vector number {next_index} for span '{span}' of entity {entity_qid}")
        return next_index
        #? SAVE THE INDEX NOW ???

        

    def similarity(self, A: str, Bs: List[str]) -> float:
        """
        Calculates similarity between A and each of B, returns maximum
        """
        A = A.lower()
        return max([SequenceMatcher(None, A, B.lower()).ratio() for B in Bs])

  