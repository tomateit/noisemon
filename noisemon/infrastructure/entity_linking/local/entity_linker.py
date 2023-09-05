"""
One and only module that opetares with faiss index and performs vector search
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union, Optional, Any
from functools import partial as p

import faiss
import torch
import numpy as np
import pandas as pd

from noisemon.domain.models.entity_span import EntitySpan
from noisemon.logger import logger
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import MentionData
from noisemon.tools.char_span_to_vector import ContextualEmbedding
from noisemon.tools.flat_map import flat_map
from noisemon.tools.tools import get_majority_by
from noisemon.tools.similarity import similarity
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker


cwd = Path(__file__).resolve()

@dataclass
class MemoryData:
    entity_qid: str
    span: str
    vector: np.ndarray

def validate_input_data(data: Any):
    assert isinstance(data, np.ndarray), f"Input data must be `np.ndarray` but it is {type(data)}"
    assert data.dtype == np.float32, f"Tensor shall have dtype np.float32, but has {data.dtype}"


class EntityLinkerLocalImpl(EntityLinker):
    model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
    memory_path = cwd / "entity_liner_memory.parquet"

    vector_index: faiss.IndexFlatIP | None = None
    number_of_dimensions = 0
    index_dataframe: pd.DataFrame | None = None
    entity_groups = None
    contextual_embedder = None

    memory_columns = ["entity_qid", "span", "vector"]

    def __init__(
            self,
            k_neighbors: int = 4,
            cutoff_threshold: float = 0.95,
            memory_path: Path | None = None,
    ):
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        if memory_path is not None:
            self.memory_path = memory_path

    def initialize(self):
        logger.debug("Initializer contextual embedder")
        self.contextual_embedder = ContextualEmbedding(model_name=self.model_name)

        logger.debug("Vector loading has been launched")
        dataframe = pd.read_parquet(self.memory_path, columns=self.memory_columns)
        if len(dataframe) == 0:
            logger.warning("No vectors to add in index. Add vectors!")
            return

        # inferring dimensionality from data
        sample = dataframe.iloc[0]
        sample_vector = sample["vector"]
        number_of_dimensions = len(sample_vector)
        self.number_of_dimensions = number_of_dimensions

        # assigning integer indices
        dataframe.reset_index(drop=True, inplace=True)

        # separating the vectors
        tensor = np.vstack(dataframe.vectors)
        dataframe.drop(columns=["vector"], inplace=True)

        # sticking the dataframes to the instance
        self.index_dataframe = dataframe
        self.entity_groups = dataframe.groupby("entity_qid")

        # initializing the index itself
        self.vector_index = faiss.IndexFlatIP(self.number_of_dimensions)
        self.vector_index.add(tensor)

        logger.info(f"Index trained: {self.vector_index.is_trained}, number of vectors: {self.vector_index.ntotal}")
        logger.debug("EntityLinker initialized")


    def find_closes_indices(self, vector) -> list[int]:
        validate_input_data(vector)
        D, I = self.vector_index.search(vector, self.k_neighbors)
        return I[0].astype(int).tolist()

    def find_closes_indices_batch(self, tensor: np.ndarray) -> List[List[int]]:
        validate_input_data(tensor)
        D, I = self.vector_index.search(tensor, self.k_neighbors)
        return I.astype(int).tolist()

    def get_entity_by_vector_index(self, index: int) -> EntityData | None:
        if not index >= 0: return None
        entity_qid = self.index_dataframe.loc[index]["entity_qid"]
        return EntityData(qid=entity_qid)

    def get_entity_aliases(self, entity: EntityData) -> list[str]:
        return self.entity_groups.get_group(entity.qid)

    def link_entities(self, text: str, recognized_entities: list[EntitySpan]) -> list[EntityData]:
        """
        TODO
        """
        if not recognized_entities: return []

        # Entities that were matched to QID
        linked_entities: List[Union[EntityData, None]] = []

        # 1. ENTITY SPAN TO VECTOR TRANSFORM
        self.contextual_embedder.embed_text(text)
        char_spans = [(e.span_start, e.span_end) for e in recognized_entities]
        entity_vectors_list = self.contextual_embedder.get_char_span_vectors(char_spans, preserve_embedding=False)
        tensor_of_entities: np.ndarray = np.vstack(entity_vectors_list).astype(np.float32)
        logger.debug(f"For provided entity spans, got following embedding matrix: {tensor_of_entities.shape}")

        # index search shall be in one operation cuz fast
        # I is (len(ents), k)
        I: List[List[int]] = self.find_closes_indices_batch(tensor_of_entities)
        list_of_candidate_lists: List[List[Optional[MentionData]]] = flat_map(self.get_entity_by_vector_index, I)

        # 3. Strategy: choosing majority
        for recognized_entity, candidate_list in zip(recognized_entities, list_of_candidate_lists):
            if not any(candidate_list):  # all candidates may be none, we ask for at least one
                linked_entities.append(None)
                logger.debug(f"Entity {recognized_entity} has no matching candidates")
                continue

            previously_known_mention, count = get_majority_by(candidate_list, "entity_qid")
            # even if each entity appears 1 time this will be leftmost thus closest
            major_entity: EntityData = previously_known_mention.entity
            logger.debug(f"Vector of entity {recognized_entity} is close to the vectors of {major_entity.name}")
            # We can not just return any QID we got from vector query.
            # If the entity is completely unknown there still will be a result
            # Thus check span to be alike one of QID aliases
            aliases = self.get_entity_aliases(major_entity)
            if similarity(recognized_entity.span, aliases) < self.cutoff_threshold:
                # fail case
                linked_entities.append(None)
                logger.debug(f"FAIL >> Entity {recognized_entity} failed similarity test with {major_entity.name} aliases")
            else:
                # success case
                linked_entities.append(major_entity)
                logger.debug(f"SUCC >> Entity recognized as one of {major_entity.name} aliases {aliases} ")

        return linked_entities



