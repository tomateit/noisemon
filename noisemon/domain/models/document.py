import uuid
from dataclasses import dataclass


@dataclass(kw_only=True)
class DocumentData:
    resource_link_id: uuid.UUID
    document_id: uuid.UUID | None = None
    raw_content: str | None = None  # original document data
    content: str | None = None  # processed document data
    raw_text: str | None = (
        None  # unprocessed extracted text, probably with platform-specific markup
    )
    text: str | None = None  # content as processed text


@dataclass(kw_only=True)
class PersistedDocumentData(DocumentData):
    document_id: uuid.UUID
