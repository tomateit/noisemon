"""
One and only module that opetares with faiss index and performs vector search
"""
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
import pandas as pd

from noisemon.domain.models.entity import EntityData
from noisemon.logger import logger
from noisemon.domain.services.repository.repository import Repository

cwd = Path(__file__).resolve().parent
def validate_input_data(data):
    assert isinstance(data, np.ndarray), f"Input data must be `np.ndarray` but it is {type(data)}"
    assert data.dtype == np.float32, f"Tensor shall have dtype np.float32, but has {data.dtype}"

@dataclass
class MemoryData:
    entity_qid: str
    span: str
    vector: list[float]

class RepositoryLocalImpl(Repository):
    memory_path = cwd / "entity_linker_memory.parquet"

    vector_index: faiss.IndexFlatIP | None = None
    number_of_dimensions = 0
    index_dataframe: pd.DataFrame | None = None
    entity_groups = None
    memory_columns = ["entity_qid", "span", "vector"]
    def __init__(self, k_neighbors: int = 5):
        self.k_neighbors = k_neighbors


    def initialize(self):
        logger.debug("Vector loading has been launched")
        dataframe = pd.read_parquet(self.memory_path, columns=self.memory_columns)
        if len(dataframe) == 0:
            logger.warning("No vectors to add in index. Add vectors!")
            return

        # inferring dimensionality from data
        sample = dataframe.iloc[0]
        sample_vector = sample["vector"]
        number_of_dimensions = len(sample_vector)
        self.number_of_dimensions = number_of_dimensions

        # assigning integer indices
        dataframe.reset_index(drop=True, inplace=True)

        # separating the vectors
        tensor = np.vstack(dataframe["vector"])
        dataframe.drop(columns=["vector"], inplace=True)

        # sticking the dataframes to the instance
        self.index_dataframe = dataframe
        self.entity_groups = dataframe.groupby("entity_qid")

        # initializing the index itself
        self.vector_index = faiss.IndexFlatIP(self.number_of_dimensions)
        self.vector_index.add(tensor)

        logger.info(f"Index trained: {self.vector_index.is_trained}, number of vectors: {self.vector_index.ntotal}")
        logger.debug("EntityLinker initialized")

    def find_closest_indices(self, vector) -> list[int]:
        validate_input_data(vector)
        D, I = self.vector_index.search(vector, self.k_neighbors)
        return I[0].astype(int).tolist()

    def find_closes_indices_batch(self, tensor: np.ndarray) -> list[list[int]]:
        validate_input_data(tensor)
        D, I = self.vector_index.search(tensor, self.k_neighbors)
        return I.astype(int).tolist()

    def get_entity_by_vector_index(self, index: int) -> EntityData | None:
        if not index >= 0: return None
        entity_qid = self.index_dataframe.loc[index]["entity_qid"]
        return EntityData(entity_qid=entity_qid)




    def get_entity_aliases(self, entity: EntityData) -> list[str]:
        return self.entity_groups.get_group(entity.entity_qid)["span"].unique().tolist()