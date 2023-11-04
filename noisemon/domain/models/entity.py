from dataclasses import dataclass

from noisemon.domain.models.qid import EntityQID


@dataclass(kw_only=True)
class EntityData:
    entity_qid: EntityQID

