#!/usr/bin/env python
# coding: utf-8
from sqlalchemy import select, create_engine

import torch
import typer
import numpy as np
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session
from tqdm import tqdm

from noisemon.domain.models.entity_span import EntitySpanData
from noisemon.infrastructure.language_vectorization.contextual_embedder import ContextualEmbedderLocalImpl
from noisemon.infrastructure.repository_postgres.database_models import DocumentORMModel, MentionORMModel
from noisemon.logger import logger
from noisemon.settings import Settings



logger = logger.getChild("populating_vectors")


def main():
    settings = Settings()
    database_uri = str(settings.DATABASE_URI)
    device = torch.device("cuda:0")
    model_name = settings.TEXT_VECTORIZATION_MODEL_NAME
    embedder = ContextualEmbedderLocalImpl(model_name=model_name, device=device)
    engine = create_engine(database_uri)
    connection = engine.connect()
    db = Session(connection)
    limit = 60000
    # count_statement = select(func.count(MentionORMModel)).where(MentionORMModel.vector == None)
    # documents_count = db.scalar(count_statement)
    documents_count = limit

    logger.info(f"Got {documents_count} documents to recreate vectors for")

    statement = (
        select(DocumentORMModel)
        .join(DocumentORMModel.mentions)
        .limit(limit)
    )
    # statement = statement.execution_options(yield_per=1000)
    result = db.scalars(statement)
    pbar = tqdm(total=documents_count)
    success = 0
    failure = 0
    for document_model in result:
        document_model: DocumentORMModel
        mentions: list[MentionORMModel] = document_model.mentions
        spans = [
            EntitySpanData(
                span=m.span,
                span_start=m.span_start,
                span_end=m.span_end,
            )
            for m in mentions
        ]
        mention_vectors: list[torch.Tensor] = embedder.get_char_span_vectors(document_model.raw_text or document_model.text, spans)
        mention_vectors: list[np.ndarray] = [t.numpy() for t in mention_vectors]

        try:
            for mention, vector in zip(mentions, mention_vectors):
                with db.begin_nested():
                    mention.vector = vector

            db.commit()
        except DataError as ex:
            logger.exception(ex)
            failure += 1
            pbar.update(1)
            continue
        success += 1
        pbar.update(1)
        pbar.set_description(f"SUCC: [{success}], FAIL: [{failure}]")

    logger.info("Vectors are stored in database")
    connection.close()


if __name__ == "__main__":
    typer.run(main)
