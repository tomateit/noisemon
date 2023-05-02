#!/usr/bin/env python
# coding: utf-8
from typing import List, Tuple
from pathlib import Path
from collections import defaultdict
from sqlalchemy import select, func

import torch
import typer
import numpy as np
from tqdm import tqdm

from noisemon.database.database import SessionLocal
from noisemon.logger import logger
from noisemon.models.mention import MentionModel
from noisemon.models.document import DocumentModel
from noisemon.models.entity import EntityModel
from noisemon.tools.char_span_to_vector import ContextualEmbedding



def main():
    device = torch.device("cuda:0")
    model_name = "Jean-Baptiste/roberta-large-ner-english"
    embedder = ContextualEmbedding(model_name=model_name, device=device)
    db = SessionLocal()
    limit = 1000
    # count_statement = select(func.count(DocumentModel.id)).join(DocumentModel.mentions).limit(10)
    # documents_count = db.scalar(count_statement)
    documents_count = limit

    logger.info(f"Got {documents_count} documents to recreate vectors for")

    statement = select(DocumentModel).join(DocumentModel.mentions).limit(limit)
    statement = statement.execution_options(yield_per=500)
    result = db.scalars(statement)
    pbar = tqdm(total=documents_count)
    for document_model in result:
        document_model: DocumentModel
        mentions: list[MentionModel] = document_model.mentions
        embedder.embed_text(document_model.text)
        spans = [(e.span_start, e.span_end) for e in mentions]
        mention_vectors: list[torch.Tensor] = embedder.get_char_span_vectors(spans)
        mention_vectors: list[np.ndarray] = [t.numpy() for t in mention_vectors]

        for mention, vector in zip(mentions, mention_vectors):
            with db.begin_nested():
                mention.vector = vector

        pbar.update(1)

    logger.info("Vectors are stored in database")


if __name__ == "__main__":
    typer.run(main)
