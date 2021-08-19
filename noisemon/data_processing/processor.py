import zmq
from models.data_chunk import DataChunk
import logging
import spacy

class Processor():
    socket: zmq.Socket
    context: zmq.Context
    # nlp: spacy.lang.ru.Russian

    def __init__(self):
        # self.nlp = spacy.load("ru_core_news_lg")
        pass

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
        # doc = self.nlp(data)
        # for ent in doc.ents:
        #     print(ent.text, ent.start_char, ent.end_char, ent.label_)
        print(data)