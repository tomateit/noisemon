import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import logging
from pathlib import Path
from collections import defaultdict

import spacy

import crud
from schemas import DataChunk
from models import Entity, Mention, VectorIndex
from database import SessionLocal, engine
from ner_extractor import NerExtractor
from entity_linker import EntityLinker
from dataset_populator import DatasetPopulator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Processor:
    def __init__(self):
        self.nlp_ru = spacy.load("ru_core_news_lg")
        self.db = SessionLocal()
        self.ner_extractor = NerExtractor(nlp=self.nlp_ru)

        self.entity_linker = EntityLinker()
        self.dataset_populator = DatasetPopulator(self.entity_linker, self.nlp_ru)



    def process_data(self, data: DataChunk):
        text = data.raw_text

        doc = self.nlp_ru.make_doc(text)
        # 1. Entity Linking phase
        doc = self.ner_extractor.extract(doc)

        # 2. Detect named entities
        named_entities = [entity for entity in doc.ents if entity.label_ == "ORG"]
        entity_spans = [
            (entity.start_char, entity.end_char) for entity in named_entities
        ]
        logger.debug(f"Detected entities: {named_entities}")
        # 3. Match named entities with KB entities
        entities: Entity = self.entity_linker.link_entities(text, entity_spans)
        assert len(named_entities) == len(
            entities
        ), f"Each span shall be matched with entity or None"

        # 4. Store mentions in database
        mentions = defaultdict(list)
        for named_entity, entity in zip(named_entities, entities):
            if entity:
                mentions[entity].append(named_entity.text)

        for entity, matched_entities in mentions.items():
            logger.debug(f"Detected mention of {entity.qid} as {matched_entities}")
            crud.create_entity_mention(
                self.db, entity, data.timestamp, source=data.link
            )

        logger.debug(f"Recognized entities: {[x.name for x in mentions.keys()]}")

        # 4. Try populating knowledgebase
        if named_entities:
            # we do not actually assume that processor and dataset_populator
            # must have the same NER module, but it is
            self.dataset_populator.populate(text, [], [])
