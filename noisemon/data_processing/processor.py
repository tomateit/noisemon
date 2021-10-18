import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from pathlib import Path
from collections import defaultdict
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
        self.ner_extractor = NerExtractor(nlp=self.nlp) 
        self.ticker_processor = TickerProcessor()
        self.entity_linker = EntityLinker(
            faiss_index_path = Path("./bin/2021-10-17-12-58-54_faiss_index_222_vectors.binary"),
            index_to_qid_map_path = Path("./bin/2021-10-17-12-58-54_index_to_qid_mapping.json"),
            qid_to_aliases_path = Path("./bin/2021-10-17-12-58-54_qid_to_aliases_mapping.json"),
        )

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
        
        # 2. Ticker matching phase
        # tickers = self.ticker_processor.extract_tickers(text)
        # 2.1 For tickers extract company names
        # company_names = list(map(self.ticker_processor.lookup_ticker_in_knowledgebase, tickers))
        # company_to_ticker_map = dict(zip(company_names, tickers))
        # 3. Match them with extracted organizations
        # matched_pairs, unmatched_orgs, unmatched_tickers = self.entity_linker.match_names(ners, company_to_ticker_map)
        # CASE 1 : everything exactly matched -> horray, populate training dataset
        # CASE 2 : some of NERS do not exist in tickets -> human check, penalize NER
        # CASE 3 : ???

        # 4. Match entity spans with QIDs
        entities = [entity for entity in doc.ents if entity.label_ == "ORG"]
        entity_spans = [(entity.start_char, entity.end_char) for entity in entities]
        print("Detected entities: ", entities)
        qids = self.entity_linker.link_entities(text, entity_spans)                    
        
        mentions = defaultdict(list)
        
        for entity, qid in zip(entities, qids):
            if qid:
                mentions[qid].append(entity.text)

        for qid, matched_entities in mentions.items():
            print(f"Detected mention of {qid} as {matched_entities}")
            crud.create_entity_mention(self.db, qid, data["timestamp"], source=data["origin"])
        
        print("Recognized entities: ", list(mentions.keys()))
        print()