import json
import sys
sys.path.append("noisemon")
from typing import Optional
from pathlib import Path
from functools import lru_cache
from pprint import pprint

import typer
from tqdm import tqdm
from wasabi import Printer

from noisemon.database import SessionLocal
from noisemon.crud import create_entity, get_all_vector_index_qids
from noisemon.data_processing.wikidata import Wikidata
from noisemon.schemas import EntityType
msg = Printer()


def main(cache_path: Path):
    wikidata = Wikidata()
    db = SessionLocal()
    qids = get_all_vector_index_qids(db)
    cache = json.loads(cache_path.read_text()) if cache_path.exists() and cache_path.is_file() else {}
    db.commit()

    for qid in tqdm(qids):
        query_qid = qid
        if "http:" in query_qid:
            query_qid = qid.split("/")[-1]
        if query_qid not in cache:
            cache[query_qid] = wikidata.lookup_entity_label_by_qid(query_qid)
        label = cache[query_qid]
        if not label:
            continue
        
        create_entity(
            db=db,
            qid=qid,
            entity_name=label,
            type=EntityType.ORGANIZATION
        )
        

    db.commit()
    db.close()
    msg.good("Finished populating")

    if cache_path.is_dir():
        out_cache = cache_path / "qid_to_label.json"
        with open(out_cache, "w") as fout:
            json.dump(cache, fout, ensure_ascii=False)
        msg.good(f"Saved cache to {out_cache}")



if __name__ == "__main__":
    typer.run(main)