#!/usr/bin/env python
# coding: utf-8
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

    embedder = ContextualEmbedding()
    qid_to_vector_list = defaultdict(list)
    qid_to_alias = defaultdict(set)

    for labelstudio in tqdm(data):
        # Process data
        qid_aliass, qid_vecs = ann_to_ent(labelstudio, embedder=embedder)
        # Merge results
        for QID, vecs in qid_vecs.items():
            qid_to_vector_list[QID].extend(vecs)
        for QID, aliases in qid_aliass.items():
            qid_to_alias[QID].update(aliases)

    msg.info(f"Result contains {sum([len(v) for v in qid_to_vector_list.values()])} vectors")

    vector_index_to_qid = {}
    vectors_tensor = []

    index = 0
    for qid, vectors in qid_to_vector_list.items():
        for vector in vectors:
            vector_index_to_qid[index] = qid
            index += 1
            vectors_tensor.append(vector)
            
    vectors_tensor = torch.vstack(vectors_tensor)
    
    d = 768  # dimension   
    faiss_index = faiss.IndexFlatIP(d)   # build the index
    faiss_index.add(vectors_tensor.numpy()) # add vectors to the index
    
    index_output_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_faiss_index_" + str(faiss_index.ntotal) + "_vectors.binary"
    output = str(output_folder/index_output_name)
    faiss.write_index(faiss_index, output)
    msg.good("Index was build and saved successfully", "Location: " + output)

    mapping_output_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_index_to_qid_mapping.json"
    output = str(output_folder/mapping_output_name)
    with open(output, "w") as fout:
        json.dump(vector_index_to_qid, fout)
    msg.good("Vector index to qid mapping was saved", "Location: " + output)

    aliases_output_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "_qid_to_aliases_mapping.json"
    output = str(output_folder/aliases_output_name)
    qid_to_alias = {qid: list(aliases) for qid, aliases in qid_to_alias.items()}
    with open(output, "w") as fout:
        json.dump(qid_to_alias, fout)
    msg.good("QID to aliases mapping was saved successfully", "Location: " + output)



def ann_to_ent(labelstudio, embedder) -> Tuple[Dict[str, Set[str]], Dict[str, List[torch.Tensor]]]:
    """
    Given labelstudio data returns two dicts: Dict[QID, {Alias}] and Dict[QID, [Vector]]
    """
    # Temporary structures
    id_to_qid_name_pair = defaultdict(dict)
    qid_and_span_pairs = [] # [(qid, (span_s,span_e))]
    # Result buffers
    qid_to_vector_list = defaultdict(list)
    qid_to_alias = defaultdict(set)
    
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
            qid_to_alias[QID].add(entity)
            # vecs will be calculated later
            qid_and_span_pairs.append((QID, (entity_start, entity_end)))
            
    # Given spans, get context vectors
    qids, spans = zip(*qid_and_span_pairs) # [(qid, span), (qid, span)] -> [qid, qid], [span, span]
    entity_vectors = embedder.get_char_span_vectors(spans)
    for QID, entity_vector in zip(qids, entity_vectors):
        qid_to_vector_list[QID].append(entity_vector)
    
    return qid_to_alias, qid_to_vector_list



if __name__ == "__main__":
    typer.run(main)
