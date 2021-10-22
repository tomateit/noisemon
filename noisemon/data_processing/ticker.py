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
    explicit_dollarsign_ticker = regex.compile("(?<=\$)[A-Z]{1,5}")
    def __init__(self):
        self.extractor = reticker.TickerExtractor()
        
        

    def extract_tickers(self, text: str) -> List[str]:
        """
        Takes a text, returns a list of strigs, that appear like tickers
        Just simple regex extraction
        """
        ticker_set = set(self.extractor.extract(text))

        return list(ticker_set)
