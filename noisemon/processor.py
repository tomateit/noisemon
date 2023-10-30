import typer

from noisemon.domain.services.repository.repository import Repository
from noisemon.logger import logger
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.entity_span import EntitySpan

from noisemon.domain.services.entity_recognition.entity_recognizer import EntityRecognizer
from noisemon.domain.services.entity_linking.entity_linker import EntityLinker

from noisemon.infrastructure.entity_recognition.local.entity_recognizer import EntityRecognizerLocalImpl
from noisemon.infrastructure.entity_linking.local.entity_linker import EntityLinkerLocalImpl


class Processor:
    def __init__(
            self,
            entity_recognizer: EntityRecognizer,
            entity_linker: EntityLinker,
            repository: Repository,
        ):
        self.entity_recognizer = entity_recognizer
        self.entity_linker = entity_linker

    def process_data(self, text: str):

        recognized_entities: list[EntitySpan] = self.entity_recognizer.recognize_entities(text)
        logger.debug(f"Recognized entities: {recognized_entities}")

        linked_entities: list[EntityData, None] = self.entity_linker.link_entities(text, recognized_entities)

        for recognized_entity, lined_entity in zip(recognized_entities, linked_entities, strict=True):
            print(f"Entity: {recognized_entity.span} | {lined_entity.qid}")

        print("---------")


if __name__ == "__main__":
    entity_linker = EntityLinkerLocalImpl()
    entity_linker.initialize()
    processor = Processor(
        entity_recognizer=EntityRecognizerLocalImpl(),
        entity_linker=entity_linker,
    )

    def main(text: str):
        processor.process_data(text)

    typer.run(main)


