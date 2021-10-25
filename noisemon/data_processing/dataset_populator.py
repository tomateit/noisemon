"""
This module is separated so, 
bc dataset population is a learning-time feature with
it's specific design and strategy considerations,
which do not acually fit the overall application.

The dataset population consist of the following important cases:
1. Creating new entities with all relevant work
    - creating new vectors in faiss (performed by entity_linker module as responsible for faiss operations)
    - creating new Entities in db with their names
2. Creating partially-labeled data for further manual checks and extending train data
"""
import json
import regex
from pathlib import Path
import crud
from data_processing.ticker import TickerProcessor
from data_processing.wikidata import Wikidata
from database import SessionLocal, engine
from schemas import EntityType
from scripts.char_span_to_vector import ContextualEmbedding
# from scripts.convert_to_labelstudio import from_text_ner_nel
from datetime import datetime
DATA_PATH = Path("./data/generated_examples").resolve()
assert DATA_PATH.exists(), f"Path {DATA_PATH} does not exist, we are in {Path().resolve()}"

class DatasetPopulator():
        def __init__(self, entity_linker, nlp):
            self.ticker_processor = TickerProcessor()
            self.wikidata = Wikidata()
            self.db = SessionLocal()
            self.embedder = ContextualEmbedding()
            self.entity_linker = entity_linker
            self.nlp = nlp

        def populate(self, text, entities_recognized, entities_not_recognized):
            self.ticker_strategy(text, entities_recognized, entities_not_recognized)

        def base_strategy(self, text, entities_recognized, entities_not_recognized):
            """
            Basic strategy extends KB (vector storage) by storing vecs of successfully identified entities
            Thus (hopefully) extending quality of further lookups and disabmiguations
            """
            #TODO
            pass
        
        def ticker_strategy(self, text, entities_recognized, entities_not_recognized) -> None:
            """
            Match tickers with entities, create new entities from matched, add new vectors
            """
            # Design decidion: quit the function asap - avoid heavy calls
        
            # 1. Extract entities and tickers and match them
            #TODO This actually duplicates what was done in main processing cycle
            doc = self.nlp(text)
            entities = [entity for entity in doc.ents if entity.label_ =="ORG"]
            print(f"Detected Entities: {entities}")
            if not entities:
                return
            
            tickers = self.ticker_processor.extract_tickers(text)
            print(f"Detected Tickers: {tickers}")
            if not tickers:
                return
            # We do not know, which ticker belongs to which ORG at all,
            # So it's reasonable to perform lookup through all aliases
            possible_orgs = {} # QID : {set of aliases}
            for ticker in tickers:
                lookup_result = self.wikidata.lookup_aliases_by_ticker(ticker)
                possible_orgs.update(lookup_result)
            # this can erase some entities with overlapping aliases, but let it be so for now
            reverse_index = {alias.lower(): qid for qid, alias_set in possible_orgs.items() for alias in alias_set}
            
            organizations_matched = []
            organizations_mismatched = []
            self.embedder.embed_text(text)
            #TODO similarity calctulation
            #from difflib import SequenceMatcher
            #SequenceMatcher(None, "газпром", "газпромом").ratio()
            for entity in entities:
                QID = reverse_index.get(entity.text.lower(), None)
                if QID:
                    organizations_matched.append((entity, QID))
                else:
                    organizations_mismatched.append(entity)
                    
            print(f"Matched: {organizations_matched}")
            print(f"Mismatched: {organizations_mismatched}")
            entity_spans = [(entity.start_char, entity.end_char) for (entity, QID) in organizations_matched]
            entity_vectors = self.embedder.get_char_span_vectors(entity_spans)
            # 2. For matched entities, 
            for (org_entity, QID), vector in zip(organizations_matched, entity_vectors):
                # ... ensure DB has such entity
                org_name = self.wikidata.lookup_entity_label_by_qid(QID)
                try:
                    crud.create_entity(self.db, QID, org_name, type=EntityType.ORGANIZATION)
                    print(f"Created new entity: {QID} as {org_name}")
                except Exception as e:
                    print(e)
                    
                # ... store vector in KB and DB
                # entity_qid: str, vector: np.ndarray, span: str
                vector = vector.numpy().reshape((1, -1))
                self.entity_linker.add_entity_vector(entity_qid = QID, vector= vector, span=org_entity.text)
                

                


            # # 4. Results shall be converted into labelstudio-compatible form for human check
            # labelstudio_example = from_text_ner_nel(text, entities, organizations_matched)
            # with open(DATA_PATH / f"{datetime.now().isoformat()}.json", "w") as fout:
            #     json.dump(labelstudio_example, fout, ensure_ascii=False)