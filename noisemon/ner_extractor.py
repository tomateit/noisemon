import logging
from typing import List, Tuple

import spacy


class NerExtractor():

    def __init__(self, nlp=None):
        if not nlp:
            self.nlp = spacy.load("ru_core_news_lg")
        else:
            self.nlp=nlp
        

    def extract(self, doc: spacy.tokens.Doc) -> spacy.tokens.Doc:
        """
        Takes a Doc, applies Ner pipeline on it
        Currently takes just ORG type
        """
        doc = self.nlp.get_pipe("ner")(doc)
                
        return doc