import datetime
import uuid
from dataclasses import dataclass

from pydantic import AnyHttpUrl


@dataclass(kw_only=True)
class ResourceLinkData:
    # Resources
    resource_id: uuid.UUID
    name: str
    uri: AnyHttpUrl | None
    publication_timestamp: datetime.datetime


@dataclass(kw_only=True)
class PersistedResourceLinkData(ResourceLinkData):
    # Resources
    resource_link_id: uuid.UUID
