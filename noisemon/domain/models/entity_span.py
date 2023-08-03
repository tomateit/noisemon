from dataclasses import dataclass


@dataclass(kw_only=True)
class EntitySpan:
    span: str
    span_start: int
    span_end: int
