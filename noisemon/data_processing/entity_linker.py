from typing import List, Dict, Tuple
from knowledge_base.storage import MyKnowledgeBase
import spacy

class EntityLinker():
    def __init__(self, nlp=None):
        if not nlp:
            self.nlp = spacy.load("ru_core_news_lg")
        else:
            self.nlp = nlp
        self.kb = MyKnowledgeBase()

    def link_entities(self, doc: spacy.tokens.Doc) -> spacy.tokens.Doc:
        """
        Populates spacy doc entities with knowledge base references
        """
        doc = self.nlp.get_pipe("entity_linker")(doc)
        return doc


    def match_names(self, ners, name_map: Dict[str, str]) -> Tuple[List, List, List]:
        """
        
        """

        return 

  
