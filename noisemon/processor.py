from typing import List, Union
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import logging
from pathlib import Path
from collections import defaultdict

import spacy

# import crud
from schemas import DataChunk
from models import Entity, Mention
from database import SessionLocal, engine
from entity_recognizer import EntityRecognizer
from entity_linker import EntityLinker
from dataset_populator import DatasetPopulator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Processor:
    def __init__(self):
        model_path = (Path(__file__).parent / "training/nlp_trf-2.0.0/model-best").resolve()
        self.nlp = spacy.load(model_path)
        self.db = SessionLocal()
        # self.entity_recognizer = EntityRecognizer(nlp=self.nlp)
        self.entity_linker = EntityLinker()
        self.dataset_populator = DatasetPopulator(self.entity_linker, self.nlp)



    def process_data(self, data: DataChunk):
        # 1. Save data to database

        # 2. Implicit NER
        text = data.raw_text
        doc = self.nlp(text)
        recognized_entities = [entity for entity in doc.ents if entity.label_ == "ORG"]
        logger.debug(f"Recognized entities: {recognized_entities}")

        # 3. Match named linked_entities with KB linked_entities
        linked_entities: List[Union[Entity, None]] = self.entity_linker.link_entities(doc)
        assert len(recognized_entities) == len(linked_entities), f"Each span shall be matched with entity or None"

        # 4. Store mentions in database
        mentions = defaultdict(list)
        for named_entity, entity in zip(recognized_entities, linked_entities):
            if entity:
                mentions[entity].append(named_entity.text)

        for entity, matched_entities in mentions.items():
            logger.debug(f"Detected mention of {entity.qid} as {matched_entities}")
            Mention.create_entity_mention(self.db, entity, data.timestamp, source=data.link)

        logger.debug(f"Linked entities: {[x.name for x in mentions.keys()]}")

        # 5. Try populating knowledgebase
        if recognized_entities:
            # we do not actually assume that processor and dataset_populator
            # must have the same NER module, but it is
            self.dataset_populator.populate(doc)
