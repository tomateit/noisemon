from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
from typing import List, Dict
from time import sleep
from urllib.error import HTTPError
import logger

class Wikidata:
    def __init__(self):
        self.sparql = SPARQLWrapper("http://query.wikidata.org/sparql")
        self.sparql.setReturnFormat(JSON)

    def lookup_companies_by_ticker(self, ticker: str) -> List:

        query = """
            SELECT DISTINCT ?id ?idLabel ?ISIN WHERE {
                SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
                VALUES ?ticker { "%s"}
                ?id p:P414 ?exchange.
                ?exchange pq:P249 ?ticker.
                # OPTIONAL { 
                #     ?exchange p:P946 ?ISIN
                # }
            }
            LIMIT 20""" % (ticker,)
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
        except HTTPError as e:
            if e.code == 429:
                timeout = 10
                logger.debug(f"Encountered 429 from wikidata. Gonna sleep for {timeout} and retry")
                sleep(10)
                return self.lookup_companies_by_ticker(ticker)

        return results["results"]["bindings"]
