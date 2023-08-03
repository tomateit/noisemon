"""
Schemas file is used for external contract and data shape specification
For application-wide models use noisemon.models
"""

from pydantic import BaseModel


class DataChunk(BaseModel):
    # origin: str
    link: str
    text: str
    raw_text: str
    timestamp: str # datetime is not json serializable

    # class Config:
    #     orm_mode = True



# class Entity(BaseModel):
#     name: str
#     type: EntityType

