from typing import List, Dict, Set, Optional
from collections import defaultdict
import logging
from time import sleep
from pprint import pprint
from urllib.error import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF

from tools.cache_to_redis import get_cacher
from settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

redis_params = {
    "host":settings.REDIS_HOST,
    "port":settings.REDIS_PORT,
    "db":settings.REDIS_DB,
    "client_name":"wikidata_cache",
}
redis_cacher = get_cacher(redis_params, EXPIRE=60*60*24*7)
decorator = redis_cacher(key_argument_position=1)

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
                logger.debug(f"Encountered 429 from wikidata. Gonna sleep for {timeout} and retry")
                sleep(timeout)
                return retried_function(*args, **kwargs)
            else:
                raise
    return retried_function

class Wikidata:
    def __init__(self):
        self.sparql = SPARQLWrapper("http://query.wikidata.org/sparql")
        self.sparql.setReturnFormat(JSON)

    # @retry_request
    # @redis_cacher(key_argument_position=1)
    def lookup_companies_by_ticker(self, ticker: str) -> List:
        """
        Given string ticker returns a list of junk
        """
        print("Obsolete")
        return []


    # @redis_cacher(key_argument_position=1)
    @retry_request
    @decorator
    def lookup_entity_label_by_qid(self, qid) -> Optional[str]:
        """
        Given QID, lookup for name in russian (fallback to english)
        """
        logger.debug(f"Performing wikidata entities lookup by QID: {qid}")
        if "http" in qid:
            qid = qid.split("/")[-1]
        query =  """
            SELECT DISTINCT ?label WHERE {
                wd:%s rdfs:label ?label FILTER (lang(?label)="ru" || lang(?label)="en").
            }
            LIMIT 1""" % (qid)
        
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
    
        if not results["results"]["bindings"]:
            return None
        return results["results"]["bindings"][0]["label"]["value"]

    # @redis_cacher
    @decorator
    @retry_request
    def lookup_aliases_by_ticker(self, ticker: str) -> Dict[str, List[str]]:
        """
        Given ticker, lookup for aliases and return em with respect to
        entity QID, e.g. Dict[QID, List of aliases (unique)]
        """
        logger.debug(f"Performing wikidata entity aliases lookup given ticker: {ticker}")
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
            res[x["id"]["value"]].add(x["alias"]["value"])
        for x in results["results"]["bindings"]:
            res[x["id"]["value"]].add(x["idLabel"]["value"])

        res = {key: list(value) for key, value in res.items()}
        return res