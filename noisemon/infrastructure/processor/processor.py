from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.entity_span import EntitySpanData
from noisemon.domain.models.mention import MentionData
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker
from noisemon.domain.services.entity_recognition.entity_recognizer import (
    EntityRecognizer,
)
from noisemon.domain.services.language_detection.language_detector import (
    LanguageDetector,
)
from noisemon.domain.services.language_representation.contextual_embedder import (
    ContextualEmbedder,
)
from noisemon.domain.services.processor.processor import Processor
from noisemon.domain.services.repository.repository import Repository
from noisemon.logger import logger


class ProcessorImpl(Processor):
    def __init__(
        self,
        entity_recognizer: EntityRecognizer,
        entity_linker: EntityLinker,
        language_detector: LanguageDetector,
        repository: Repository,
        contextual_embedder: ContextualEmbedder,
    ):
        self.entity_recognizer = entity_recognizer
        self.entity_linker = entity_linker
        self.repository = repository
        self.contextual_embedder = contextual_embedder
        self.language_detector = language_detector

    def process_document(self, document: DocumentData):
        # 0. Language Recognition
        language = self.language_detector.detect_language(document.text)
        if language is None:
            logger.warning("Unsupported language")
            return []

        # 1. Entity Recognition
        recognized_entities: list[EntitySpanData] = (
            self.entity_recognizer.recognize_entities(document.text)
        )
        logger.debug(f"Recognized entities: {recognized_entities}")

        # 2. EntitySpan -> MentionData
        vectors = self.contextual_embedder.get_char_span_vectors(
            document.text, recognized_entities
        )
        mentions = [
            MentionData(
                span_start=es.span_start,
                span_end=es.span_end,
                span=es.span,
                vector=vec,
            )
            for es, vec in zip(recognized_entities, vectors, strict=True)
        ]

        # 3. Entity Linking
        linked_entities: list[EntityData | None] = self.entity_linker.link_entities(
            mentions, document
        )

        for recognized_entity, linked_entity in zip(
            recognized_entities, linked_entities, strict=True
        ):
            logger.debug(
                f"Entity: {recognized_entity.span} | {linked_entity and linked_entity.entity_qid}"
            )

        return [le for le in linked_entities if le is not None]
