import json
from dataclasses import asdict
from pathlib import Path

import torch
import typer
import pandas as pd
from tqdm import tqdm

from noisemon.domain.models.document import DocumentData, PersistedDocumentData
from noisemon.domain.models.entity import EntityData
from noisemon.domain.models.qid import EntityQID
from noisemon.domain.models.resource import ResourceDataTO
from noisemon.settings import settings
from noisemon.domain.models.mention import MentionData
from noisemon.infrastructure.language_vectorization.contextual_embedder import ContextualEmbedderLocalImpl
from noisemon.infrastructure.repository_postgres.repository import RepositoryPostgresImpl


def main(dataset_path: Path):
    # IMPORT DATA
    texts_df = pd.read_parquet(dataset_path / "texts.parquet")
    mentions_df = pd.read_parquet(dataset_path / "mentions.parquet")
    resource_description = ResourceDataTO.model_validate(json.loads(Path(dataset_path / "resource.json").read_text())).to_dataclass()
    mention_groups = mentions_df.groupby("text_id")
    pbar = tqdm(total=len(texts_df))

    # Embedder
    encoder = ContextualEmbedderLocalImpl(device=torch.device("cuda:0"))
    repository = RepositoryPostgresImpl(settings.DATABASE_URI)

    resource = repository.persist_new_resource(resource_description)
    assert resource.resource_id is not None

    memory_buffer = []
    for idx, text_row in texts_df.iterrows():
        # text_row: original_text, id
        new_document = DocumentData(
            text=text_row["original_text"],
            document_tag=text_row["text_id"],
        )
        document: PersistedDocumentData = repository.persist_new_document(new_document)


        mentions_subframe = mention_groups.get_group(text_row["text_id"])

        mentions = []
        text = document.text
        for idx, mention_row in mentions_subframe.iterrows():
            entity_qid = EntityQID(mention_row.entity_qid)
            mention = MentionData(
                document_id=document.document_id,
                entity_qid=entity_qid,
                span_start=mention_row.span_start,
                span_end=mention_row.span_end,
                span=mention_row.span,
                vector=None
            )
            mentions.append(mention)

        for mention in mentions:
            entity = EntityData(entity_qid=mention.entity_qid)
            repository.persist_new_entity(entity)

        vectors = encoder.get_char_span_vectors(text, mentions)
        for mention, vector in zip(mentions, vectors, strict=True):
            # some of the spans could be truncated
            # their vector will contain nans
            if torch.isnan(vector).any():
                continue

            mention.vector = vector.tolist()

        mentions = [m for m in mentions if m.vector is not None]

        for mention in mentions:
            repository.persist_new_mention(mention, document)

        pbar.update(1)

    print("Done")

    pbar.close()


if __name__ == "__main__":
    typer.run(main)

