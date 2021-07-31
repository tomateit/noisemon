from pydantic import BaseModel

class DataChunk(BaseModel):
    origin: str
    text: str
    raw_text: str