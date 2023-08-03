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
from typing import List, Optional

from noisemon.database.wikidata import Wikidata
from noisemon.database.database import SessionLocal
from noisemon.models import EntityModel
from noisemon.dataset_population.ticker_strategy import ticker_strategy

class DatasetPopulator:
    def __init__(self, entity_linker, nlp):
        self.wikidata = Wikidata()
        self.db = SessionLocal()
        self.entity_linker = entity_linker
        self.nlp = nlp

    def populate(self, text, linked_entities: List[Optional[EntityModel]]):
        """Entry point"""
        ticker_strategy(text, linked_entities)



