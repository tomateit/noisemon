from dataclasses import dataclass
from typing import Optional

# def generate_uuid():
#     return str(uuid.uuid4())
#

@dataclass(kw_only=True)
class EntityData:
    qid: str


