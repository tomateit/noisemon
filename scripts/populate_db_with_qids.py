from typing import Optional
import sqlite3
import typer
from pathlib import Path
import json
from functools import lru_cache
from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, RDF
sparql = SPARQLWrapper("http://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
from tqdm import tqdm
from wasabi import Printer
msg = Printer()

# __tablename__ = "entities"
# qid = Column(String, name="qid", primary_key=True)
# name = Column(String, unique=False, index=True)
# type = Column(Enum(EntityType))


def main(database_path: Path, qid_file_path: Path, cache_location: Optional[Path] = None):
    assert database_path.exists(), "Database must exist"
    assert qid_file_path.exists(), "QID file must exist"
    msg.info(f"Loaded database {str(database_path)}")
    qids = list(json.loads(qid_file_path.read_text()).keys())
    cache = json.loads(cache_location.read_text()) if cache_location and cache_location.exists() else {}
    conection = sqlite3.connect(database_path)
    cursor = conection.cursor()

    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS entities
                (qid text, name text, type text)''')

    for qid in tqdm(qids):
        if qid not in cache:
            cache[qid] = qid_to_label(qid)
        label = cache[qid]
        if not label:
            continue
        # Insert a row of data
        try:
            cursor.execute("INSERT INTO entities VALUES ('%s','%s', 'org')" % (qid, label))
        except sqlite3.IntegrityError:
            pass
    # Save (commit) the changes
    conection.commit()
    conection.close()
    msg.good("Finished populating")

    out_cache = qid_file_path.parent /"qid_label_cache.json"
    with open(out_cache, "w") as fout:
        json.dump(cache, fout, ensure_ascii=False)
    msg.good(f"Saved cache to {out_cache}")

def qid_to_label(qid: str) -> Optional[str]:
    query =  """
        SELECT DISTINCT ?label WHERE {
            wd:%s rdfs:label ?label FILTER (lang(?label)="ru").
        }
    LIMIT 1""" % (qid)
    sparql.setQuery(query)
    results = sparql.query().convert()
    if not results["results"]["bindings"]:
        print(f"No label for '{qid}'")
        return None
    return results["results"]["bindings"][0]["label"]["value"]

if __name__ == "__main__":
    typer.run(main)