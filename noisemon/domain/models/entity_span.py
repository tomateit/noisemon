from dataclasses import dataclass


@dataclass(kw_only=True)
class EntitySpanData:
    span: str
    span_start: int
    span_end: int
