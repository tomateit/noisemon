from pathlib import Path

import typer
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import balanced_accuracy_score

from noisemon.domain.models.entity_span import EntitySpanData
from noisemon.infrastructure.entity_linking.local.entity_linker import EntityLinkerImpl


def evaluate_entity_linking(test_data_dir: Path, whitelist_path: Path):
    shared_entities = set(pd.read_parquet(whitelist_path)["qid"].values)
    entity_linker = EntityLinkerImpl()
    entity_linker.initialize()

    mentions_df = pd.read_parquet(test_data_dir / "mentions.parquet")
    texts_df = pd.read_parquet(test_data_dir / "texts.parquet")

    texts_df = texts_df.sample(5000)

    print("Mentions: \n", mentions_df.info())
    print("Texts: \n", texts_df.info())

    mention_groups = mentions_df.groupby("text_id")

    true_buffer = []
    predicted_buffer = []

    for _, row in tqdm(texts_df.iterrows(), total=len(texts_df)):
        mentions_group = mention_groups.get_group(row.text_id)
        mentions_group = mentions_group.to_dict(orient="records")
        mentions_group = [
            m for m in mentions_group if m["entity_qid"] in shared_entities
        ]
        if not mentions_group:
            continue

        mentions: list[EntitySpanData] = [
            EntitySpanData(
                span_start=m["span_start"], span_end=m["span_end"], span=m["span"]
            )
            for m in mentions_group
        ]
        true_entities_str: list[str] = [m["entity_qid"] for m in mentions_group]
        raise NotImplementedError

        linked_entities = entity_linker.link_entities(row.original_text, mentions)
        linked_entities_str = [e.entity_qid if e else "NONE" for e in linked_entities]

        true_buffer.extend(true_entities_str)
        predicted_buffer.extend(linked_entities_str)

    baccuracy = balanced_accuracy_score(true_buffer, predicted_buffer)
    print(f"Balanced Accuracy with no adjustment (just weighted): {baccuracy}")

    baccuracy_adj = balanced_accuracy_score(
        true_buffer, predicted_buffer, adjusted=True
    )
    print(f"Balanced Accuracy with adjustment (random=0, perfect=1): {baccuracy_adj}")


if __name__ == "__main__":
    typer.run(evaluate_entity_linking)
