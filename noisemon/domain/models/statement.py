from dataclasses import dataclass

from noisemon.domain.models.entity import EntityData

@dataclass(kw_only=True)
class Statement:
    subject: EntityData | str
    predicate: str
    object: EntityData | str
    