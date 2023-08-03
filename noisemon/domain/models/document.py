from dataclasses import dataclass, asdict
from typing import Optional, Literal
from datetime import datetime

from noisemon.database.database import Base

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


# class DocumentModel(Base):
#     __tablename__ = "documents"
#     id = Column(String, name="id", primary_key=True, default=generate_uuid)
#     origin = Column(JSONB, name="origin")
#
#     text = Column(String, nullable=False)
#     raw_text = Column(String, nullable=False)
#
#     mentions = relationship("MentionModel", back_populates="origin")


# def model_to_dataclass(o: DocumentModel) -> DocumentData:
#     return DocumentData(
#         id=o.id,
#         origin=DocumentOrigin(**o.origin),
#         text=o.text,
#         raw_text=o.raw_text,
#     )

# def dataclass_to_model(o: DocumentData):
#     return DocumentModel(
#         origin=asdict(o.origin),
#         text=o.text,
#         raw_text=o.raw_text,
#     )