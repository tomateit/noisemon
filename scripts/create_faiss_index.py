#!/usr/bin/env python
# coding: utf-8
import sys
sys.path.append("noisemon")
from typing import List, Dict, Set, Tuple
import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import torch
import typer
import faiss
import numpy as np
from tqdm import tqdm
from wasabi import Printer
from noisemon.crud import create_vector_index
from noisemon.database import SessionLocal, engine

try:
    from scripts.char_span_to_vector import ContextualEmbedding
except ImportError:
    from .char_span_to_vector import ContextualEmbedding

msg = Printer()

def main(data_path: Path, output_folder: Path):
    assert data_path.exists() and not data_path.is_dir(), "Data_path must be an existing file"
    assert output_folder.exists() and output_folder.is_dir(), "Output_folder must be an existing folder"

    data = json.loads(data_path.read_text())
    msg.info(f"Got {len(data)} labeling results")
    database = SessionLocal()

    embedder = ContextualEmbedding()

    all_qids, all_aliases, all_vectors = [], [], []
    for labelstudio in tqdm(data):
        # Process data
        list_of_qids, list_of_aliases, list_of_vectors = ann_to_ent(labelstudio, embedder=embedder)
        # Merge results
        for QID, alias, vector in zip(list_of_qids, list_of_aliases, list_of_vectors):
            all_qids.extend(list_of_qids)
            all_aliases.extend(list_of_aliases)
            all_vectors.extend(list_of_vectors)


    msg.info(f"Result contains {len(all_vectors)} vectors")
    assert len(all_qids) == len(all_aliases) == len(all_vectors)

    
             
    vectors_tensor = torch.vstack(all_vectors)
    
    d = 768  # dimension   
    faiss_index = faiss.IndexFlatIP(d)   # build the index
    faiss_index.add(vectors_tensor.numpy()) # add vectors to the index
    
    index_output_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_faiss_index_" + str(faiss_index.ntotal) + "_vectors.binary"
    output = str(output_folder/index_output_name)
    faiss.write_index(faiss_index, output)
    msg.good("Index was build and saved successfully", "Location: " + output)

    for idx, (qid, alias) in enumerate(zip(all_qids, all_aliases)):
        create_vector_index(db = database, entity_qid = qid, index = idx, span = alias, source = "dataset")
    msg.good("Vector index to qid and alias mapping was added to database")

    
    



def ann_to_ent(labelstudio, embedder) -> Tuple[List[str], List[str], List[torch.Tensor]]:
    """
    Given labelstudio data returns three list of equal length: QIDs, Text span, Vector
    """
    # Temporary structures
    id_to_qid_name_pair = defaultdict(dict)
    list_of_spans = [] # [(span_s,span_e))]
    # Result buffers
    list_of_qids = []
    list_of_vectors = []
    list_of_aliases = []
    
    
    text = labelstudio["data"]["text"]
    embedder.embed_text(text)
    
    # 1. Matching labeling result chunks by their labelstudio internal IDs
    for chunk in labelstudio["annotations"][0]["result"]:
        if chunk["from_name"] == "ner":
            id_to_qid_name_pair[chunk["id"]]["text"] = chunk["value"]["text"]
        if chunk["from_name"] == "entity":
            id_to_qid_name_pair[chunk["id"]]["qid"] = chunk["value"]["text"][0]

    # 2. Match QIDs with respecting spans and text chunks (aliases)
    for chunk in labelstudio["annotations"][0]["result"]:
        if chunk["from_name"] == "ner":
            QID = id_to_qid_name_pair[chunk["id"]].get("qid", None)
            if not QID:
                print(f"{id_to_qid_name_pair[chunk['id']]['text']} has no matching QID")
                continue
            # aliases
            entity_start, entity_end = chunk["value"]["start"], chunk["value"]["end"]
            entity = text[entity_start: entity_end]
            list_of_aliases.append(entity)
            # vecs will be calculated later
            list_of_spans.append((entity_start, entity_end))
            list_of_qids.append(QID)
            
    # Given spans, get context vectors
    list_of_vectors = embedder.get_char_span_vectors(list_of_spans)
        
    assert len(list_of_aliases) == len(list_of_vectors) == len(list_of_qids)

    return list_of_qids, list_of_aliases, list_of_vectors



if __name__ == "__main__":
    typer.run(main)
