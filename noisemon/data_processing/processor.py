import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import logging
from pathlib import Path
from collections import defaultdict

import zmq
import spacy

import crud
from schemas import DataChunk
from models import Entity, Mention, VectorIndex
from database import SessionLocal, engine
from data_processing.ner_extractor import NerExtractor
from data_processing.entity_linker import EntityLinker
from data_processing.dataset_populator import DatasetPopulator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Processor:
    socket: zmq.Socket
    context: zmq.Context
    # nlp: spacy.lang.ru.Russian

    def __init__(self):
        self.nlp = spacy.load("ru_core_news_lg")
        self.db = SessionLocal()
        self.ner_extractor = NerExtractor(nlp=self.nlp)

        self.entity_linker = EntityLinker()
        self.dataset_populator = DatasetPopulator(self.entity_linker, self.nlp)

    def connect_to_queue(self):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.bind("tcp://127.0.0.1:2001")
        self.socket.subscribe("")
        # self.socket.setsockopt(zmq.SUBSCRIBE, "")

    def run(self):
        logger.debug("Processing is launched")
        if not hasattr(self, "socket"):
            self.connect_to_queue()

        while True:
            data = self.socket.recv_json()
            logger.debug(f"Recieved data from socket: {data}")
            self.process_data(data)
        # for data in await self.socket.recv_json():
        #     self.process_data(data)

    def process_data(self, data: DataChunk):
        text = data["raw_text"]

        doc = self.nlp.make_doc(text)
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
                mentions[entity].append(entity.text)

        for entity, matched_entities in mentions.items():
            logger.debug(f"Detected mention of {entity.qid} as {matched_entities}")
            crud.create_entity_mention(
                self.db, entity, data["timestamp"], source=data["origin"]
            )

        logger.debug(f"Recognized entities: {[x.name for x in mentions.keys()]}")

        # 4. Try populating knowledgebase
        if named_entities:
            self.dataset_populator.populate(text, [], [])
