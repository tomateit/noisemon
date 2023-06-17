from abc import ABCMeta

from noisemon.domain.services.entity_linking.entity_linker import EntityLinker
from noisemon.domain.services.entity_recognition.entity_recognizer import EntityRecognizer


class Processor(metaclass=ABCMeta):
    def __init__(
            self,
            entity_recognizer: EntityRecognizer,
            entity_linker: EntityLinker,
            # rdf_converter: RDFConverter,
        ):
        ...

    def process(self, text: str) -> list["Triplet"]:
        ...