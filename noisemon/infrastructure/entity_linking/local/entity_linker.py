"""
One and only module that opetares with faiss index and performs vector search
"""
from typing import List, Union, Optional
from functools import partial as p

import torch
import numpy as np

from noisemon.domain.models.entity_span import EntitySpan
# import crud
from noisemon.logger import logger
from noisemon.vector_index import VectorIndex
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import MentionData
from noisemon.tools.flat_map import flat_map
from noisemon.tools.tools import get_majority_by
from noisemon.tools.similarity import similarity
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker


class EntityLinkerLocalImpl(EntityLinker):
    vector_index = None

    def __init__(
            self,
            k_neighbors: int = 4,
            cutoff_threshold: float = 0.95,
    ):
        # self.d = self.embedder.d  # dimension
        self.d = 768
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold

    def initalize(self):
        self.vector_index = VectorIndex(self.d)

        logger.debug("EntityLinker initialized")

    def get_entity_by_vector_index(self, index: int) -> EntityData:
        return EntityData()

    def get_entity_aliases(self, entity) -> list[str]:
        return ["Microsoft", "MSFT"]

    def link_entities(self, text: str, recognized_entities: list[EntitySpan]) -> list[EntityData]:
        """
        TODO
        """
        # Entities that were matched to QID
        linked_entities: List[Union[EntityData, None]] = []

        if not recognized_entities: return []

        # 1. ENTITY VECTORS LOOKUP
        # Not all entities have vectors. E.g. if an emoji is recognized as one, it is not in transformer's vocab
        entity_vectors_list: list[torch.Tensor] = [ent["vector"].numpy() for ent in recognized_entities]
        tensor_of_entities: np.ndarray = np.vstack(entity_vectors_list).astype(np.float32)
        logger.debug(f"For provided entity spans, got following embedding matrix: {tensor_of_entities.shape}")

        # index search shall be in one operation cuz fast
        # I is (len(ents), k)
        I: List[List[int]] = self.vector_index.find_closes_indices_batch(tensor_of_entities, self.k_neighbors)
        list_of_candidate_lists: List[List[Optional[MentionData]]] = flat_map(self.get_entity_by_vector_index, I)

        # 3. Strategy: choosing majority
        for recognized_entity, candidate_list  in zip(recognized_entities, list_of_candidate_lists):
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
