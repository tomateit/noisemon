from pydantic import BaseModel

from noisemon.domain.models.entity import EntityModel


class Triplet(BaseModel):
    subject: EntityModel | str
    predicate: str
    object: EntityModel| str