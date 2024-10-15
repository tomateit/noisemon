import datetime
import uuid
from dataclasses import dataclass
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, AwareDatetime


class ResourceTypes(str, Enum):
    dataset = "dataset"
    website = "website"
    telegram_channel = "telegram_channel"


@dataclass(kw_only=True)
class ResourceData:
    resource_id: uuid.UUID
    resource_type: ResourceTypes
    resource_name: str
    uri: str
    created_at: datetime.datetime


class ResourceDataTO(BaseModel):
    resource_id: uuid.UUID
    resource_type: ResourceTypes
    resource_name: str
    uri: AnyHttpUrl
    created_at: AwareDatetime

    def to_dataclass(self):
        return ResourceData(
            resource_id=self.resource_id,
            resource_type=self.resource_type,
            resource_name=self.resource_name,
            uri=str(self.uri),
            created_at=self.created_at,
        )
