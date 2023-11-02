from dataclasses import asdict
from pathlib import Path

import torch
import typer
import pandas as pd
from tqdm import tqdm

from noisemon.domain.models.document import DocumentData
from noisemon.settings import settings
from noisemon.domain.models.mention import MentionData
from noisemon.infrastructure.language_representation.contextual_embedder import ContextualEmbedderLocalImpl
from noisemon.infrastructure.repository_postgres.repository import RepositoryPostgresImpl


def main(text_dataframe_path: Path, mentions_dataframe_path: Path):
    # IMPORT DATA
    texts_df = pd.read_parquet(text_dataframe_path)
    mentions_df = pd.read_parquet(mentions_dataframe_path)
    mention_groups = mentions_df.groupby("text_id")
    pbar = tqdm(total=len(texts_df))

    # Embedder
    encoder = ContextualEmbedderLocalImpl(device=torch.device("cuda:0"))
    repository = RepositoryPostgresImpl(settings.DATABASE_URI)

    memory_buffer = []
    for idx, text_row in tqdm(texts_df.iterrows(), total=len(texts_df)):
        # text_row: original_text, id
        document = DocumentData(text=text_row.original_text, document_id=text_row.id)
        document = repository.persist_new_document(document)


        mentions_subframe = mention_groups.get_group(text_row["text_id"])
        mentions = []
        text = text_row["original_text"]
        for idx, mention_row in mentions_subframe.iterrows():
            mention = MentionData(
                entity_qid=mention_row.entity_qid,
                span_start=mention_row.span_start,
                span_end=mention_row.span_end,
                span=mention_row.span,
                vector=None
            )
            mentions.append(mention)

        vectors = encoder.get_char_span_vectors(text, mentions)
        for mention, vector in zip(mentions, vectors, strict=True):
            mention.vector = vector.tolist()

        for mention in mentions:
            repository.persist_new_mention(mention, document)

        pbar.update(1)

    print("Done")

    pbar.close()



if __name__ == "__main__":
    typer.run(main)

