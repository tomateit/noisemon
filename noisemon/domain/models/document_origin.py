import datetime
from dataclasses import dataclass


@dataclass(kw_only=True)
class DocumentOrigin:
    source_name: str
    source_url: str
    uri: str
    retrieval_timestamp: datetime.datetime
