import torch
import typer

from noisemon.infrastructure.language_detection.language_detector import (
    LanguageDetectorLocalImpl,
)
from noisemon.logger import logger
from noisemon.settings import settings

# data
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.entity_span import EntitySpan
from noisemon.domain.models.document import DocumentData
from noisemon.domain.models.mention import MentionData

# abstracts
from noisemon.domain.services.consumer.consumer import Consumer
from noisemon.domain.services.processor.processor import Processor
from noisemon.domain.services.repository.repository import Repository
from noisemon.domain.services.entity_recognition.entity_recognizer import (
    EntityRecognizer,
)
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker
from noisemon.domain.services.language_representation.contextual_embedder import (
    ContextualEmbedder,
)

# implementations
from noisemon.infrastructure.processor.processor import ProcessorImpl
from noisemon.infrastructure.consumer.consumer_queue import ConsumerQueueImpl
from noisemon.infrastructure.entity_linking.local.entity_linker import EntityLinkerImpl
from noisemon.infrastructure.repository_postgres.repository import (
    RepositoryPostgresImpl,
)
from noisemon.infrastructure.entity_recognition.local.entity_recognizer import (
    EntityRecognizerLocalImpl,
)
from noisemon.infrastructure.language_vectorization.contextual_embedder import (
    ContextualEmbedderLocalImpl,
)


def actor(
    consumer: Consumer,
    repository: Repository,
    processor: Processor,
):
    for document in consumer.get_new_document():
        try:
            mentions: list[MentionData] = processor.process_document(document)
        except Exception as ex:
            msg = f"Could not process the document: {ex}"
            logger.exception(msg, exc_info=1)
            consumer.nack_last_document()
            continue

        try:
            persisted_document = repository.persist_new_document(document)
        except Exception as ex:
            msg = f"Could not persist the document: {ex}"
            logger.exception(msg, exc_info=1)
            consumer.nack_last_document()
            continue

        try:
            for mention in mentions:
                repository.persist_new_mention(mention, persisted_document)
        except Exception as ex:
            msg = f"Could not process document: {ex}"
            logger.exception(msg, exc_info=1)
            consumer.nack_last_document()
            continue

        consumer.ack_last_document()


def start_queue_to_database():
    contextual_embedder = ContextualEmbedderLocalImpl(device=torch.device("cpu"))
    language_detector = LanguageDetectorLocalImpl()
    entity_recognizer = EntityRecognizerLocalImpl(device=torch.device("cpu"))
    repository = RepositoryPostgresImpl(settings.DATABASE_URI)
    consumer = ConsumerQueueImpl(
        settings.RABBITMQ_URI,
        settings.RABBITMQ_EXCHANGE,
        settings.RABBITMQ_SOURCE_QUEUE,
    )

    entity_linker = EntityLinkerImpl(repository=repository)

    processor = ProcessorImpl(
        entity_recognizer=entity_recognizer,
        entity_linker=entity_linker,
        repository=repository,
        contextual_embedder=contextual_embedder,
        language_detector=language_detector,
    )

    try:
        actor(consumer=consumer, processor=processor, repository=repository)
    except Exception as ex:
        logger.exception(str(ex))
    finally:
        consumer.graceful_shutdown()


if __name__ == "__main__":
    start_queue_to_database()
