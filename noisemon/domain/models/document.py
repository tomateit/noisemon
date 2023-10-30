from dataclasses import dataclass
from typing import Optional


#
# def generate_uuid():
#     return str(uuid.uuid4())


# @dataclass(kw_only=True)
# class DocumentOrigin:
#     from_process: Literal["news_stream", "kb_population"]
#     link: Optional[str] = None
#     resource: Optional[str] = None
#     timestamp: Optional[datetime] = None


@dataclass(kw_only=True)
class DocumentData:
    # origin: DocumentOrigin
    text: str   # content as text
    raw_text: str  # content in raw form, probably with platform-specific markup
    id: Optional[str] = None


