"""
One and only module that opetares with faiss index and performs vector search
"""
from typing import List, Union, Optional
from functools import partial as p

import torch
import numpy as np
try:
    from spacy.tokens import Doc, Span
except ImportError:
    pass

# import crud
from noisemon.logger import logger
from noisemon.vector_index import VectorIndex
from noisemon.models.entity import EntityModel
from noisemon.models.mention import MentionModel
from noisemon.database.database import SessionLocal
from noisemon.tools.flat_map import flat_map
from noisemon.tools.tools import get_majority_by
from noisemon.tools.similarity import similarity


class EntityLinker:
    def __init__(
            self,
            k_neighbors: int = 4,
            cutoff_threshold: float = 0.95,
    ):
        # self.d = self.embedder.d  # dimension
        self.d = 768
        self.db = SessionLocal()
        self.vector_index = VectorIndex(self.d)
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        logger.debug("EntityLinker initialized")

    def link_entities_raw(self, recognized_entities: list[dict]) -> List[Union[EntityModel, None]]:
        """
        'Basically maps doc.ents -> to -> wikidata ents'
        Links provided doc ents with known entities and returns a list of `Entity` models.
        If a span text does not resemble any of QID aliases, will return `None`, otherwise `Entity`.
        Doc must contain ._.trf_data to get span embeddings
        The resulting list is of the same length as doc.ents
        """
        # Entities that were matched to QID
        linked_entities: List[Union[EntityModel, None]] = []
        # All detected entities of type
        recognized_entities: list[dict] = [ent for ent in recognized_entities
                                           if ent["entity_group"] == "ORG"]
        if not recognized_entities: return []
        # 1. ENTITY VECTORS LOOKUP
        # Not all entities have vectors. E.g. if an emoji is recognized as one, it is not in transformer's vocab
        entity_vectors_list: list[torch.Tensor] = [ent["vector"].numpy() for ent in recognized_entities]
        tensor_of_entities: np.ndarray = np.vstack(entity_vectors_list).astype(np.float32)
        logger.debug(f"For provided entity spans, got following embedding matrix: {tensor_of_entities.shape}")

        # index search shall be in one operation cuz fast
        # I is (len(ents), k)
        I: List[List[int]] = self.vector_index.find_closes_indices_batch(tensor_of_entities, self.k_neighbors)
        list_of_candidate_lists: List[List[Optional[MentionModel]]] = flat_map(p(MentionModel.get_by_vector_index, self.db), I)

        # pprint(list_of_candidate_lists)

        # 3. Strategy: choosing majority
        for candidate_list, recognized_entity in zip(list_of_candidate_lists, recognized_entities):
            if not any(candidate_list):  # all candidates may be none, we ask for at least one
                linked_entities.append(None)
                logger.debug(f"Entity {recognized_entity} has no matching candidates")
                continue

            previously_known_mention, count = get_majority_by(candidate_list, "entity_qid")
            # even if each entity appears 1 time this will be leftmost thus closest
            major_entity: EntityModel = previously_known_mention.entity
            logger.debug(f"Vector of entity {recognized_entity} is close to the vectors of {major_entity.name}")
            # We can not just return any QID we got from vector query.
            # If the entity is completely unknown there still will be a result
            # Thus check span to be alike one of QID aliases
            if similarity(recognized_entity["word"], major_entity.aliases) < self.cutoff_threshold:
                linked_entities.append(None)
                logger.debug(
                    f"FAIL >> Entity {recognized_entity} failed similarity test with {major_entity.name} aliases")
            else:
                # 1. Increment number of matches for a vector
                previously_known_mention.number_of_matches += 1
                self.db.add(previously_known_mention) # TODO probaby shall be a refresh
                linked_entities.append(major_entity)
                logger.debug(f"SUCC >> Entity recognized as one of {major_entity.name} aliases {major_entity.aliases} ")

        return linked_entities


    def link_entities(self, doc) -> List[Union[EntityModel, None]]:
        """
        'Basically maps doc.ents -> to -> wikidata ents'
        Links provided doc ents with known entities and returns a list of `Entity` models.
        If a span text does not resemble any of QID aliases, will return `None`, otherwise `Entity`.
        Doc must contain ._.trf_data to get span embeddings
        The resulting list is of the same length as doc.ents
        """
        # Entities that were matched to QID
        linked_entities: List[Union[EntityModel, None]] = []
        # All detected entities of type
        recognized_entities: List[Span] = [ent for ent in doc.ents
                                           if ent.label_ == "ORG" and ent._.trf_vector is not None]
        if not recognized_entities: return []

        # 1. ENTITY VECTORS LOOKUP
        # Not all entities have vectors. E.g. if an emoji is recognized as one, it is not in transformer's vocab
        entity_vectors_list: List[np.ndarray] = [ent._.trf_vector for ent in recognized_entities]
        tensor_of_entities: np.ndarray = np.vstack(entity_vectors_list).astype(np.float32)
        logger.debug(f"For provided entity spans, got following embedding matrix: {tensor_of_entities.shape}")

        # index search shall be in one operation cuz fast
        # I is (len(spans), k)
        I: List[List[int]] = self.vector_index.find_closes_indices_batch(tensor_of_entities, self.k_neighbors)
        list_of_candidate_lists: List[List[Optional[MentionModel]]] = flat_map(p(MentionModel.get_by_vector_index, self.db), I)

        # pprint(list_of_candidate_lists)

        # 3. Strategy: choosing majority
        for candidate_list, recognized_entity in zip(list_of_candidate_lists, recognized_entities):
            if not any(candidate_list):  # all candidates may be none, we ask for at least one
                linked_entities.append(None)
                logger.debug(f"Entity {recognized_entity} has no matching candidates")
                continue

            previously_known_mention, count = get_majority_by(candidate_list, "entity_qid")
            # even if each entity appears 1 time this will be leftmost thus closest
            major_entity: EntityModel = previously_known_mention.entity
            logger.debug(f"Vector of entity {recognized_entity} is close to the vectors of {major_entity.name}")
            # We can not just return any QID we got from vector query.
            # If the entity is completely unknown there still will be a result
            # Thus check span to be alike one of QID aliases
            if similarity(recognized_entity.text, major_entity.aliases) < self.cutoff_threshold:
                linked_entities.append(None)
                logger.debug(
                    f"FAIL >> Entity {recognized_entity} failed similarity test with {major_entity.name} aliases")
            else:
                # 1. Increment number of matches for a vector
                previously_known_mention.number_of_matches += 1
                self.db.add(previously_known_mention)
                linked_entities.append(major_entity)
                logger.debug(f"SUCC >> Entity recognized as one of {major_entity.name} aliases {major_entity.aliases} ")

        return linked_entities




