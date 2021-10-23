from typing import List, Dict, Set, Optional
from collections import defaultdict
import logging
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
            timeout = DEFAULT_TIMEOUT
            return function(*args, **kwargs)
            
        except HTTPError as e:
            if e.code == 429:
                timeout += 5
                logging.debug(f"Encountered 429 from wikidata. Gonna sleep for {timeout} and retry")
                sleep(timeout)
                return function(*args, **kwargs)
            else:
                raise
    return retried_function

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
            }
            LIMIT 20""" % (ticker,)
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()

        return results["results"]["bindings"]

    def lookup_entity_label_by_qid(self, qid) -> Optional[str]:
        """
        Given QID, lookup for name in russian
        """
        query =  """
            SELECT DISTINCT ?label WHERE {
                wd:%s rdfs:label ?label.
            }
            LIMIT 1""" % (qid)
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
    
        if not results["results"]["bindings"]:
            return None
        return results["results"]["bindings"][0]["label"]["value"]

    @lru_cache(maxsize=5000)
    @retry_request
    def lookup_aliases_by_ticker(self, ticker: str) -> Dict[str, Set[str]]:
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
        
        res = defaultdict(set)
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
    
        for x in results["results"]["bindings"]:
            res[x["id"]["value"].split("/")[-1]].add(x["alias"]["value"])
        for x in results["results"]["bindings"]:
            res[x["id"]["value"].split("/")[-1]].add(x["idLabel"]["value"])

        return res