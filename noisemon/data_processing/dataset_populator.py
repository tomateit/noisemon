"""
This module is separated so, 
bc dataset population is a learning-time feature with
it's specific design and strategy considerations,
which do not acually fit the overall apploication
"""
import crud
from data_processing.ticker import TickerProcessor


class DatasetPopulator():
        def __init__(self, entity_linker):
            self.ticker_processor = TickerProcessor()
# 2. Ticker matching phase



        def populate(self, text, entities_recognized, entities_not_recognized):
            self.ticker_strategy(text, entities_recognized, entities_not_recognized)
        
        def ticker_strategy(self, text, entities_recognized, entities_not_recognized):
            tickers = self.ticker_processor.extract_tickers(text)
            pass
        # 2.1 For tickers extract company names
        # company_names = list(map(self.ticker_processor.lookup_ticker_in_knowledgebase, tickers))
        # company_to_ticker_map = dict(zip(company_names, tickers))
        # 3. Match them with extracted organizations
        # matched_pairs, unmatched_orgs, unmatched_tickers = self.entity_linker.match_names(ners, company_to_ticker_map)
        # CASE 1 : everything exactly matched -> horray, populate training dataset
        # CASE 2 : some of NERS do not exist in tickets -> human check, penalize NER
        # CASE 3 : ???