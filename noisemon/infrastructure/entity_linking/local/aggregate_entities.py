from dataclasses import asdict
from pathlib import Path
import typer
import pandas as pd
from tqdm import tqdm

from noisemon.infrastructure.entity_linking.local.entity_linker import EntityLinkerLocalImpl, MemoryData
from noisemon.tools.char_span_to_vector import ContextualEmbedding


def main(text_dataframe_path: Path, mentions_dataframe_path: Path, memory_path: Path | None = None):
    texts_df = pd.read_parquet(text_dataframe_path)
    mentions_df = pd.read_parquet(mentions_dataframe_path)
    mention_groups = mentions_df.groupby("text_id")

    encoder = ContextualEmbedding(EntityLinkerLocalImpl.model_name)

    memory_buffer = []
    for idx, text_row in tqdm(texts_df.iterrows(), total=len(texts_df)):
        # text_row: original_text, id
        encoder.embed_text(text_row["original_text"])
        mentions_subframe = mention_groups.get_group(text_row.id)
        for idx, mention_row in mentions_subframe.iterrows():
            span_pair = (mention_row.span_start, mention_row.span_end)
            vector, _ = encoder.get_char_span_vectors([span_pair])
            mention = MemoryData(
                vector=vector,
                entity_qid=mention_row.entity_id,
                span=mention_row.span,
            )
            memory_buffer.append(mention)

    memory_result = pd.DataFrame([asdict(m) for m in memory_buffer])

    if memory_path:
        previous_memory = pd.read_parquet(memory_path)
        memory_result = pd.concat([previous_memory, memory_result])

    memory_result.to_parquet(EntityLinkerLocalImpl.memory_path)


if __name__ == "__main__":
    typer.run(main)

