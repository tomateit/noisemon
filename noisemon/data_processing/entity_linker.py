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

class EntityLinker():
    def __init__(
        self, 
        faiss_index_path: Path, 
        index_to_qid_map_path: Path,
        qid_to_aliases_path: Path,
        k_neighbors: int = 4,
        cutoff_threshold: float = 0.8,
        ):

        self.faiss_index = faiss.read_index(str(faiss_index_path))
        self.index_to_qid_map = json.loads(index_to_qid_map_path.read_text())
        self.qid_to_aliases = json.loads(qid_to_aliases_path.read_text())
        self.embedder = ContextualEmbedding()
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        logging.debug("EntityLinker initialized")

    def link_entities(self, text: str, spans: List[Tuple[int, int]]) -> List[Union[str, None]]:
        """
        Links provided text spans with QIDs from index and returns a list of QIDs. 
        If span does not resemple any of QID aliases, will return None. Otherwise QID
        """
        if not spans:
            return []
        detected_qids = []
        entities = [text[e[0]:e[1]] for e in spans]
        self.embedder.embed_text(text)
        entity_vectors: List[torch.Tensor] = self.embedder.get_char_span_vectors(spans)
        entity_vectors: numpy.ndarray = torch.vstack(entity_vectors).numpy()
        print("For provided entity spans, got following embeding matrix: ", entity_vectors.shape)

        _, I = self.faiss_index.search(entity_vectors, self.k_neighbors) 
        # I is (len(spans), k)
        qid_candidates: List[List[str]] = [
            [self.index_to_qid_map[str(vector_index)] for vector_index in span_vec_idx_candidates]
            for span_vec_idx_candidates in list(I)
        ]
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
            if self.similarity(entity, self.qid_to_aliases[QID]) < self.cutoff_threshold:
                QID = None
            detected_qids.append(QID)

        return detected_qids


    def similarity(self, A: str, Bs: List[str]) -> float:
        """
        Calculates similarity between A and each of B, returns maximum
        """
        A = A.lower()
        return max([SequenceMatcher(None, A, B.lower()).ratio() for B in Bs])

  