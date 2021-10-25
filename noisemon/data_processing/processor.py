import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from pathlib import Path
from collections import defaultdict
import zmq
from schemas import DataChunk
from database import SessionLocal, engine
from data_processing.ner_extractor import NerExtractor
from data_processing.entity_linker import EntityLinker
from data_processing.dataset_populator import DatasetPopulator
import logging
import spacy
import crud

class Processor():
    socket: zmq.Socket
    context: zmq.Context
    # nlp: spacy.lang.ru.Russian

    def __init__(self):
        self.nlp = spacy.load("ru_core_news_lg")
        self.db = SessionLocal()
        self.ner_extractor = NerExtractor(nlp=self.nlp) 
        
        self.entity_linker = EntityLinker(
            faiss_index_path = Path("./bin/faiss_index_1170_vectors.binary")
        )
        self.dataset_populator = DatasetPopulator(self.entity_linker, self.nlp)

    def connect_to_queue(self):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.bind("tcp://127.0.0.1:2001")
        self.socket.subscribe("")
        # self.socket.setsockopt(zmq.SUBSCRIBE, "")

    def run(self):
        logging.info("Processing is launched")
        if not hasattr(self, "socket"):
            self.connect_to_queue()
        
        while True:
            data = self.socket.recv_json()
            logging.debug("Recieved data from socket")
            self.process_data(data)
        # for data in await self.socket.recv_json():
        #     self.process_data(data)

    def process_data(self, data: DataChunk):
        text = data["raw_text"]
        print("-------------------")
        print("Text: ", text)
        doc = self.nlp.make_doc(text)
        # 1. Entity Linking phase
        doc = self.ner_extractor.extract(doc)
        # doc = self.entity_linker.link_entities(doc)
        # 2. Match entity spans with QIDs
        entities = [entity for entity in doc.ents if entity.label_ == "ORG"]
        entity_spans = [(entity.start_char, entity.end_char) for entity in entities]
        print("Detected entities: ", entities)
        qids = self.entity_linker.link_entities(text, entity_spans)                    
        
        # 3. Store mentions in database
        mentions = defaultdict(list)
        for entity, qid in zip(entities, qids):
            if qid:
                mentions[qid].append(entity.text)

        for qid, matched_entities in mentions.items():
            print(f"Detected mention of {qid} as {matched_entities}")
            crud.create_entity_mention(self.db, qid, data["timestamp"], source=data["origin"])
        
        print("Recognized entities: ", list(mentions.keys()))
        print()

        # 4. Try populating knowledgebase
        if entities:
            self.dataset_populator.populate(text, [], [])


    