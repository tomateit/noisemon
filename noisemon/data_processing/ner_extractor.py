import logging
import spacy
from typing import List, Tuple

class NerExtractor():

    def __init__(self):
        self.nlp = spacy.load("ru_core_news_lg")
        

    def extract(self, text: str) -> List[Tuple[spacy.tokens.span.Span, str]]:
        """
        Takes a text, returns a list of pairs (spacy.Span, entity label)
        Currently takes just ORG type
        """
        doc = self.nlp(text)


        entity_list = list()
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entity_list.append(ent)
                
        return entity_list