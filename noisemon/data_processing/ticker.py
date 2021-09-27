import logging
import spacy
from typing import List, Tuple
import regex
import reticker
# from data_processing.wikidata import Wikidata


class TickerProcessor():
    """
    Class extracts tickers from texts
    """
    def __init__(self):
        self.extractor = reticker.TickerExtractor()
        # self.wikidata = Wikidata()
        
        

    def extract_tickers(self, text: str) -> List[str]:
        """
        Takes a text, returns a list of strigs, that appear like tickers
        Just simple regex extraction
        """
        ticker_set = set(self.extractor.extract(text))
        
        return list(ticker_set)

    # def lookup_ticker_in_knowledgebase(self, ticker: str) -> List:
    #     #! Remove it cuz not class-specific
    #     return self.wikidata.lookup_companies_by_ticker(ticker)