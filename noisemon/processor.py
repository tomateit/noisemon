import torch
import typer

from noisemon.logger import logger
from noisemon.settings import settings
# data
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.entity_span import EntitySpan
from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.mention import MentionData
# abstracts
from noisemon.domain.services.repository.repository import Repository
from noisemon.domain.services.entity_recognition.entity_recognizer import EntityRecognizer
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker
from noisemon.domain.services.language_representation.contextual_embedder import ContextualEmbedder
# implementations
from noisemon.infrastructure.repository_postgres.repository import RepositoryPostgresImpl
from noisemon.infrastructure.entity_recognition.local.entity_recognizer import EntityRecognizerLocalImpl
from noisemon.infrastructure.entity_linking.local.entity_linker import EntityLinkerImpl
from noisemon.infrastructure.language_representation.contextual_embedder import ContextualEmbedderLocalImpl


class Processor:
    def __init__(
            self,
            entity_recognizer: EntityRecognizer,
            entity_linker: EntityLinker,
            repository: Repository,
            contextual_embedder: ContextualEmbedder,
        ):
        self.entity_recognizer = entity_recognizer
        self.entity_linker = entity_linker
        self.repository = repository
        self.contextual_embedder = contextual_embedder

    def process_data(self, text: str):
        # 0. Data Prep
        document = DocumentData(
            text=text
        )
        # 1. Entity Recognition
        recognized_entities: list[EntitySpan] = self.entity_recognizer.recognize_entities(document.text)
        logger.debug(f"Recognized entities: {recognized_entities}")

        # 0. EntitySpan -> MentionData
        vectors = self.contextual_embedder.get_char_span_vectors(document.text, recognized_entities)
        mentions = [
            MentionData(
                span_start=es.span_start,
                span_end=es.span_end,
                span=es.span,
                vector=vec,
            )
            for es, vec in zip(recognized_entities, vectors, strict=True)
        ]

        # 2. Entity Linking
        linked_entities: list[EntityData, None] = self.entity_linker.link_entities(mentions, document)

        for recognized_entity, lined_entity in zip(recognized_entities, linked_entities, strict=True):
            print(f"Entity: {recognized_entity.span} | {lined_entity.qid}")

        print("---------")


if __name__ == "__main__":
    repository = RepositoryPostgresImpl(settings.DATABASE_URI)
    entity_recognizer=EntityRecognizerLocalImpl()
    entity_linker = EntityLinkerImpl(
        repository=repository
    )
    contextual_embedder = ContextualEmbedderLocalImpl(device=torch.device("gpu"))
    processor = Processor(
        entity_recognizer=entity_recognizer,
        entity_linker=entity_linker,
        repository=repository,
        contextual_embedder=contextual_embedder
    )

    def main(text: str):
        processor.process_data(text)

    typer.run(main)


