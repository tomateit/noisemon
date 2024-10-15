import datetime
import uuid
from dataclasses import dataclass

from pydantic import AnyHttpUrl


@dataclass(kw_only=True)
class ResourceLink:
    # Resources
    resource_id: uuid.UUID
    name: str
    uri: AnyHttpUrl | None
