from typing import List, Union
import warnings

import dateparser
try:
    from spacy.tokens import Span
    from noisemon.domain.services import *
    Span.set_extension("trf_vector", default=None, force=True)
except ImportError:
    pass


from noisemon.logger import logger
from noisemon.schemas.schemas import DataChunk
from noisemon.database.database import SessionLocal

from noisemon.domain.models.entity import EntityModel
from noisemon.domain.models.mention import MentionModel
from noisemon.domain.models.document import DocumentModel

from noisemon.entity_linker import EntityLinker
from noisemon.entity_recognizer import EntityRecognizer

warnings.filterwarnings("ignore", category=UserWarning)



class Processor:
    def __init__(self):
        self.db = SessionLocal()
        self.entity_recognizer = EntityRecognizer()
        self.entity_linker = EntityLinker()

    def process_data(self, data: Union[DataChunk, DocumentModel], transient=False):
        if not transient:
            # 1. Save data to database
            document = DocumentModel(
                link=data.link,
                text=data.text,
                raw_text=data.raw_text,
                timestamp=dateparser.parse(data.timestamp)
            )
            with self.db.begin_nested():
                self.db.add(document)
                self.db.commit()
            logger.debug(f"Created new document: {data.link}")
        else:
            document = data


        recognized_entities = self.entity_recognizer.process(document)
        logger.debug(f"Recognized entities: {recognized_entities}")
        if not recognized_entities: return []

        # 3. Match named linked_entities with KB linked_entities
        linked_entities: List[Union[EntityModel, None]] = self.entity_linker.link_entities_raw(recognized_entities)
        assert len(recognized_entities) == len(linked_entities), "Each span shall be matched with entity or None"

        # 4. Try to find extra entities
        logger.warning("Datase population is disabled") #TODO fix
        # newly_created_entities = self.dataset_populator.ticker_strategy(doc, linked_entities)
        newly_created_entities = [None] * len(recognized_entities)

        # 5. Store mentions for all entities in database
        for linked_entity, recognized_entity, new_entity in zip(
                linked_entities, 
                recognized_entities,
                newly_created_entities
            ):
            if (linked_entity is None) and (new_entity is None): continue
            if linked_entity:
                marker = "from_entity_linker"
                entity = linked_entity
            elif new_entity:
                marker = "from_populator"
                entity = new_entity
            else:
                raise Exception("Unacceptable state")
            # entity = linked_entity or new_entity # one is not None for sure
            logger.debug(f"(*) {marker} New mention will be created for {entity.name} as {recognized_entity}")
            # continue
            with self.db.begin_nested():
                new_mention = MentionModel(
                    entity_qid=entity.qid,
                    origin_id=document.id,
                    span=recognized_entity["word"],
                    span_start=recognized_entity["start_char"],
                    span_end=recognized_entity["end_char"],
                    vector=recognized_entity["vector"],
                )
                self.db.add(new_mention)
                self.entity_linker.vector_index.add_entity_vector_from_mention(new_mention)
        self.db.commit()
        logger.debug("^^^^^^^^^^^^^^^ Processor.process_data finished working ^^^^^^^^^^^^^^^^^^")
