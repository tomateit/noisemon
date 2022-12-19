from typing import List, Any

import faiss
import numpy as np

from noisemon.database.database import SessionLocal
from noisemon.models import MentionModel
from noisemon.logger import logger


class VectorIndex:
    """
    Class performs all operations regarding Faiss Vector Index
    - vector search
    - vector addition
    

    The index is fully-loaded on startup from database
    """

    index: faiss.IndexFlatIP

    def __init__(self, n_features: int):
        logger.debug(
            "Initializing vector index. Call .add_vectors to fill it with vectors"
        )
        self.db = SessionLocal()
        self.n_features = n_features
        self.index = faiss.IndexFlatIP(n_features)
        self.initialize()

    def find_closes_indices(self, vector, k: int = 5) -> List[int]:
        self.validate_input_data(vector)
        D, I = self.index.search(vector, k)
        return I[0].astype(int).tolist()

    def find_closes_indices_batch(self, tensor: np.ndarray, k: int = 5) -> List[List[int]]:
        self.validate_input_data(tensor)
        D, I = self.index.search(tensor, k)
        return I.astype(int).tolist()

    def initialize(self):
        logger.debug("Vector loading has been launched")
        tensor = MentionModel.get_all_active_vectors(self.db)
        if tensor is None:
            logger.warning("No vectors to add in index. Add vectors!")
            return
        self.validate_input_data(tensor)
        self.index.add(tensor)
        logger.info(
            f"Index trained: {self.index.is_trained}, number of vectors: {self.index.ntotal}"
        )

    def add_entity_vector_from_mention(self, mention: MentionModel):
        """
        Adds a new vector from mention
        """
        next_index = self.index.ntotal
        vector = mention.vector
        self.index.add(vector)
        mention.vector_index = next_index
        logger.debug(f"Added vector #{next_index} of mention as {mention.span} to index.")

    def validate_input_data(self, data: Any, check_first_dim=False):
        assert type(data) == np.ndarray, f"Input data must be `np.ndarray` but it is {type(data)}"
        assert data.dtype == np.float32, f"Tensor shall have dtype np.float32, but has {data.dtype}"
        if check_first_dim:
            assert data.shape == (
            1, self.n_features), f"Incompatible shape: {data.shape}, expected {(1, self.n_features)}"
        else:
            assert data.shape[1] == self.n_features, f"Tensor shape mismatch: (x, {self.n_features}) -> {data.shape}"

    @property
    def ready(self):
        return self.index.ntotal > 0

    @property
    def next_index(self) -> int:
        return self.index.ntotal
