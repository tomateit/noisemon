from typing import List, Dict
from collections import defaultdict
import logger
from time import sleep
from pprint import pprint
from urllib.error import HTTPError
from functools import lru_cache

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF

def retry_request(function):
    DEFAULT_TIMEOUT = 5
    timeout = 5
    def retried_function(*args, **kwargs):
        nonlocal timeout
        try:
            function(*args, **kwargs)
            timeout = DEFAULT_TIMEOUT
        except HTTPError as e:
            if e.code == 429:
                timeout += 5
                logger.debug(f"Encountered 429 from wikidata. Gonna sleep for {timeout} and retry")
                sleep(timeout)
                return function(*args, **kwargs)
            else:
                raise

class Wikidata:
    def __init__(self):
        self.sparql = SPARQLWrapper("http://query.wikidata.org/sparql")
        self.sparql.setReturnFormat(JSON)

    @lru_cache(maxsize=2048)
    @retry_request
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
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()

        return results["results"]["bindings"]

    def lookup_companies_by_qid(self, qid):
        pass

    @lru_cache(maxsize=5000)
    @retry_request
    def lookup_aliases_given_ticker(self, ticker: str) -> Dict[str, Set[str]]:
        """
        Given ticker, lookup for aliases and return em with respect to
        entity QID, e.g. Dict[QID, Set of aliases]
        """
        query =  """
        SELECT DISTINCT ?id ?idLabel ?alias WHERE {
            SERVICE wikibase:label { bd:serviceParam wikibase:language "ru,en". }
            VALUES ?ticker { "%s"}
            
            ?id p:P414 ?exchange.
            ?exchange pq:P249 ?ticker.
            ?id skos:altLabel ?alias .
        }
        LIMIT 150""" % (ticker,)
        sparql.setQuery(query)

        res = defaultdict(set)
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
    
            for x in results["results"]["bindings"]:
                res[x["id"]["value"]].add(x["alias"]["value"])
            for x in results["results"]["bindings"]:
                res[x["id"]["value"]].add(x["idLabel"]["value"])

        except HTTPError as e:
            if e.code == 429:
                timeout = 10
                logger.debug(f"Encountered 429 from wikidata. Gonna sleep for {timeout} and retry")
                sleep(10)
                return self.lookup_aliases_given_ticker(ticker)

        return res