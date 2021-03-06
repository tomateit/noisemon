from typing import List, Union
import logging
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from pathlib import Path
from collections import defaultdict
from datetime import datetime 

import spacy
import dateparser
from spacy.tokens import Span

from schemas import DataChunk
from models import Entity, Mention, Document
from database import SessionLocal, engine
from entity_linker import EntityLinker
from dataset_populator import DatasetPopulator
from components.custom_components import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

Span.set_extension("trf_vector", default=None, force=True)

class Processor:
    def __init__(self):
        model_path = (Path(__file__).parent.parent / "training/nlp_trf-2.0.0/model-best").resolve()
        self.nlp = spacy.load(model_path)
        self.nlp.add_pipe("span_vector_assigner.v1")
        self.db = SessionLocal()
        # self.entity_recognizer = EntityRecognizer(nlp=self.nlp)
        self.entity_linker = EntityLinker()
        self.dataset_populator = DatasetPopulator(self.entity_linker, self.nlp)



    def process_data(self, data: Union[DataChunk, Document], transient=False):
        logger.debug("vvvvvvvvvvvvv Processor.process_data called vvvvvvvvvvvvvvvvvv")
        
        if not transient:
            # 1. Save data to database
            document = Document(
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
            document=data

        # 2. Implicit NER
        doc = self.nlp(document.text)
        recognized_entities = [entity for entity in doc.ents if entity.label_ == "ORG" and entity._.trf_vector is not None]
        logger.debug(f"Recognized entities: {recognized_entities}")
        if not recognized_entities: return

        # 3. Match named linked_entities with KB linked_entities
        linked_entities: List[Union[Entity, None]] = self.entity_linker.link_entities(doc)
        assert len(recognized_entities) == len(linked_entities), f"Each span shall be matched with entity or None"

        # 4. Try to find extra entities
        newly_created_entities = self.dataset_populator.ticker_strategy(doc, linked_entities)
        
        
        # 5. Store mentions for all entities in database
        for linked_entity, recognized_entity, new_entity in zip(linked_entities, recognized_entities, newly_created_entities):
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
                new_mention = Mention(
                    entity_qid=entity.qid,
                    origin_id=document.id,
                    span=recognized_entity.text,
                    span_start=recognized_entity.start_char,
                    span_end=recognized_entity.end_char,
                    vector=recognized_entity._.trf_vector,
                )
                self.db.add(new_mention)
                self.entity_linker.vector_index.add_entity_vector_from_mention(new_mention)
        self.db.commit()
        logger.debug("^^^^^^^^^^^^^^^ Processor.process_data finished working ^^^^^^^^^^^^^^^^^^")


        

