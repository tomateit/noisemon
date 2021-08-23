import zmq
from schemas import DataChunk
from database import SessionLocal, engine
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
            self.process_data(data)
        # for data in await self.socket.recv_json():
        #     self.process_data(data)

    def process_data(self, data: DataChunk):
        doc = self.nlp(data["text"])
        print(data)
        entity_set = set()
        for ent in doc.ents:
            print(ent.text, ent.label_)
            if ent.label_ == "ORG":
                entity_set.add(ent.text)
                

        for entity_text in entity_set:
            print("Detected organization: ", entity_text)
            crud.create_entity(self.db, entity_text)