from pydantic import BaseModel

class EntitySpan(BaseModel):
    span: str
    span_start: int
    span_end: int
