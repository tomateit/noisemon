from dataclasses import dataclass

# @dataclass(kw_only=True)
# class DocumentOrigin:
#     from_process: Literal["news_stream", "kb_population"]
#     link: Optional[str] = None
#     resource: Optional[str] = None
#     timestamp: Optional[datetime] = None


@dataclass(kw_only=True)
class DocumentData:
    # origin: DocumentOrigin
    document_id: str | None = None
    raw_content: str | None = None # original document data
    content: str | None = None # processed document data
    raw_text: str | None = None # unprocessed extracted text, probably with platform-specific markup
    text: str | None = None   # content as processed text


@dataclass(kw_only=True)
class PersistedDocumentData(DocumentData):
    document_id: str
