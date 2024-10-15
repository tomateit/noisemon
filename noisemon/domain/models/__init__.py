from uuid import UUID

from pydantic import AwareDatetime, PlainSerializer, HttpUrl, BeforeValidator
from typing_extensions import Annotated

TimestampType = Annotated[
    AwareDatetime, PlainSerializer(lambda x: x.isoformat(), return_type=str)
]

UUIDType = Annotated[UUID, PlainSerializer(lambda x: str(x), return_type=str)]

HTTPType = Annotated[HttpUrl, PlainSerializer(lambda x: str(x), return_type=str)]

QIDType = Annotated[
    str,
    PlainSerializer(lambda x: x.split("/")[-1], return_type=str),
    BeforeValidator(
        lambda v: v if "http" in v else f"http://www.wikidata.org/entity/{v}"
    ),
]
