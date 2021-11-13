"""
This module is separated so, 
bc dataset population is a learning-time feature with
it's specific design and strategy considerations,
which do not acually fit the overall application.

The dataset population consist of the following important cases:
1. Creating new entities with all relevant work
    - creating new vectors (performed by entity_linker module as responsible for faiss operations)
    - creating new Entities in db with their names
"""
import logging
import regex
from pathlib import Path
from datetime import datetime
from sqlite3 import IntegrityError

import crud
from ticker import TickerProcessor
from wikidata import Wikidata
from database import SessionLocal, engine
from schemas import EntityType
from tools.char_span_to_vector import ContextualEmbedding

# from scripts.convert_to_labelstudio import from_text_ner_nel
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DatasetPopulator:
    def __init__(self, entity_linker, nlp):
        self.ticker_processor = TickerProcessor()
        self.wikidata = Wikidata()
        self.db = SessionLocal()
        self.embedder = ContextualEmbedding()
        self.entity_linker = entity_linker
        self.nlp = nlp

    def populate(self, text, entities_recognized, entities_not_recognized):
        """Entry point"""
        self.ticker_strategy(text, entities_recognized, entities_not_recognized)

    def ticker_strategy(
        self, text, entities_recognized, entities_not_recognized
    ) -> None:
        """
        Match tickers with entities, create new entities from matched, add new vectors
        """
        # Design decidion: quit the function asap - avoid heavy calls
        logger.debug("Population with ticker strategy invoked")
        # 1. Extract entities and tickers and match them
        # TODO This actually duplicates what was done in main processing cycle
        doc = self.nlp(text)
        entities = [entity for entity in doc.ents if entity.label_ == "ORG"]
        if not entities:
            logger.debug(f"No entities detected. Quitting the strategy")
            return
        logger.debug(f"Detected Entities: {entities}")

        tickers = self.ticker_processor.extract_tickers(text)
        if not tickers:
            return
        logger.debug(f"Detected Tickers: {tickers}")
        # We do not know, which ticker belongs to which ORG at all,
        # So it's reasonable to perform lookup through all aliases
        possible_orgs = {}  # QID : {set of aliases}
        for ticker in tickers:
            lookup_result = self.wikidata.lookup_aliases_by_ticker(ticker)
            possible_orgs.update(lookup_result)
        # this can erase some entities with overlapping aliases, but let it be so for now
        reverse_index = {
            alias.lower(): qid
            for qid, alias_set in possible_orgs.items()
            for alias in alias_set
        }

        organizations_matched = []
        organizations_mismatched = []
        
        # TODO similarity calctulation
        # from difflib import SequenceMatcher
        # SequenceMatcher(None, "газпром", "газпромом").ratio()
        for entity in entities:
            QID = None
            for key in reverse_index:
                if (key.lower() in entity.text.lower()) or (entity.text.lower() in key.lower()):
                    QID = reverse_index[key]
                    break
            if QID:
                organizations_matched.append((entity, QID))
            else:
                organizations_mismatched.append(entity)

        logger.debug(f"Matched: {organizations_matched}")
        logger.debug(f"Mismatched: {organizations_mismatched}")

        if not organizations_matched:
            logger.debug("None of the entities matched any of those retrived by ticker")
            return

        self.embedder.embed_text(text)
        entity_spans = [
            (entity.start_char, entity.end_char)
            for (entity, QID) in organizations_matched
        ]
        entity_vectors = self.embedder.get_char_span_vectors(entity_spans)
        # 2. For matched entities,
        entity = None
        for (org_entity, QID), vector in zip(organizations_matched, entity_vectors):
            org_name = self.wikidata.lookup_entity_label_by_qid(QID)
   
            logger.info(f"Upserting new entity: {QID} as {org_name}")
            entity = crud.create_entity(
                self.db, qid=QID, name=org_name, type=EntityType.ORGANIZATION
            )
            vector = vector.numpy().reshape((1, self.entity_linker.d))
            self.entity_linker.add_entity_vector(
                entity=entity, vector=vector, span=org_entity.text, source="online"
            )


