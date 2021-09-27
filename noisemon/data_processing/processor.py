import zmq
from schemas import DataChunk
from database import SessionLocal, engine
from data_processing.ner_extractor import NerExtractor
from data_processing.ticker import TickerProcessor
from data_processing.entity_linker import EntityLinker
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
        self.ner_extractor = NerExtractor() 
        self.ticker_processor = TickerProcessor()
        self.entity_linker = EntityLinker()

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
        # 1. Perform ticker and NER lookups
        ners = self.ner_extractor.extract(data["text"])
        tickers = self.ticker_processor.extract_tickers(data["text"])
        # 2. For tickers extract company names
        company_names = list(map(self.ticker_processor.lookup_ticker_in_knowledgebase, tickers))
        company_to_ticker_map = dict(zip(company_names, tickers))
        # 3. Match them with extracted organizations
        matched_pairs, unmatched_orgs, unmatched_tickers = self.entity_linker.match_names(ners, company_to_ticker_map)
        # CASE 1 : everything exactly matched -> horray, populate training dataset
        # CASE 2 : some of NERS do not exist in tickets -> human check, penalize NER
        # CASE 3 : ???

                      

        for entity_text in entity_set:
            print("Detected organization: ", entity_text)
            crud.create_entity(self.db, entity_text)