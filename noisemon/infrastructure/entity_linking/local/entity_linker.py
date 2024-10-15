from pathlib import Path
from typing import List, Union


from noisemon.domain.models.document import DocumentData
from noisemon.domain.services.repository.repository import Repository
from noisemon.logger import logger
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.mention import MentionData
from noisemon.tools.tools import get_majority_by
from noisemon.tools.similarity import similarity
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker


class EntityLinkerImpl(EntityLinker):
    def __init__(
        self,
        repository: Repository,
        k_neighbors: int = 20,
        cutoff_threshold: float = 0.95,
        memory_path: Path | None = None,
    ):
        self.k_neighbors = k_neighbors
        self.cutoff_threshold = cutoff_threshold
        self.repository = repository
        if memory_path is not None:
            self.memory_path = memory_path

    def candidate_decision_function(
        self, mention: MentionData, candidate_list: list[MentionData]
    ) -> EntityData | None:
        # get most frequently seen entity
        previously_known_mention, count = get_majority_by(candidate_list, "entity_qid")
        # even if each entity appears 1 time this will be leftmost thus closest
        major_entity: EntityData = previously_known_mention
        logger.debug(
            f"Vector of entity {mention} is close to the vectors of {major_entity.entity_qid}"
        )

        # We can not just return any QID we got from vector query.
        # If the entity is completely unknown there still will be a result
        # Thus check span to be alike one of QID aliases
        aliases = self.repository.get_entity_aliases_by_qid(major_entity.entity_qid)

        if similarity(mention.span, aliases) < self.cutoff_threshold:
            logger.debug(
                f"FAIL >> Entity {mention} failed similarity test with {major_entity.entity_qid} aliases: {aliases}"
            )
            return None
        else:
            # success case
            entity = self.repository.get_entity_by_qid(major_entity.entity_qid)
            logger.debug(
                f"SUCC >> Entity recognized as one of {entity} aliases {aliases} "
            )
            return entity

    def link_entities(
        self, recognized_entities: list[MentionData], document: DocumentData
    ) -> list[EntityData]:
        """
        TODO
        """
        if not recognized_entities:
            return []
        linked_entities: List[Union[EntityData, None]] = []

        # 3. Strategy: choosing majority
        for mention in recognized_entities:
            candidate_list = self.repository.get_similar_mentions(
                mention, max_mentions=self.k_neighbors
            )
            linked_entity = self.candidate_decision_function(mention, candidate_list)
            linked_entities.append(linked_entity)

        return linked_entities
