import re
from dataclasses import dataclass

from noisemon.domain.models.qid import EntityQID


@dataclass(kw_only=True)
class EntityData:
    entity_qid: EntityQID
    label: str | None
    description: str | None


def coerce_qid(entity_qid):
    # TODO: validate validity of http form
    if re.match("^http://www.wikidata.org/entity/Q\d+$", entity_qid):
        return entity_qid
    elif re.match("^Q\d+$", entity_qid):
        return f"http://www.wikidata.org/entity/{entity_qid}"
    else:
        raise ValueError(f"Unexpected QID form: {entity_qid}")
