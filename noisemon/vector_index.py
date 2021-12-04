from typing import List, Dict, Union, Any, Optional
import logging
import joblib
from pathlib import Path
from collections import Counter

import faiss
import numpy as np

from database import SessionLocal
from models import VectorIndexModel, Entity

logger = logging.getLogger("vector_index")
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)


class VectorIndex:
    """
    Class performs all operations regarding Faiss Vector Index
    - vector search
    - vector addition
    It solely operates VectorIndexModel model, to ensure that vector index is
    fully in-sync with vectors stored in database.

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

    def find_closes_indices(self, vector, k: int=5) -> List[int]:
        self.validate_input_data(vector)
        D, I = self.index.search(vector, k)
        return I[0].astype(int).tolist()

    def find_closes_indices_batch(self, tensor: np.ndarray, k: int=5) -> List[List[int]]:
        self.validate_input_data(tensor)
        D, I = self.index.search(tensor, k)
        return I.astype(int).tolist()

    def initialize(self):
        logger.debug("Vector loading has been launched")
        tensor = VectorIndexModel.get_all_active_vectors(self.db)
        self.validate_input_data(tensor)
        self.index.add(tensor)
        logger.info(
            f"Index trained: {self.index.is_trained}, number of vectors: {self.index.ntotal}"
        )

    def add_entity_vector(
        self, entity: Entity, vector: np.ndarray, span: str, source="online"
    ) -> Optional[VectorIndexModel]:
        """
        Adds a new vector into faiss, creates new VectorIndexModel entity
        If any of these actions cause error, everything will be reverted
        """
        next_vector_index = self.index.ntotal
        self.db.begin_nested()
        try:
            new_vector_index = VectorIndexModel(
                index=next_vector_index, 
                entity_qid=entity.qid, 
                vector=vector,
                span=span, 
                source=source,
            )
            self.db.add(new_vector_index)
            self.index.add(vector)
        except Exception as ex:
            logger.error(ex)
            self.db.rollback()
            return None
        self.db.commit()
        logger.debug(
            f"Added vector number {next_vector_index} for span '{span}' of entity {entity.qid}"
        )
        return new_vector_index

    def validate_input_data(self, data: Any, check_first_dim=False):
        assert type(data) == np.ndarray, f"Input data must be `np.ndarray` but it is {type(data)}"
        assert data.dtype == np.float32, f"Tensor shall have dtype np.float32, but has {data.dtype}"
        if check_first_dim:
            assert data.shape == (1,self.n_features), f"Incompatible shape: {data.shape}, expected {(1, self.n_features)}"
        else:
            assert data.shape[1] == self.n_features, f"Tensor shape mismatch: (x, {self.n_features}) -> {data.shape}"

    def get_vector_model_by_index(self, index: int) -> Optional[VectorIndexModel]:
        return VectorIndexModel.get_vector_model_by_index(self.db, index)

    def increment_number_of_mentions(self, vector_index: VectorIndexModel):
        return VectorIndexModel.increment_number_of_mentions(self.db, vector_index)

    @property
    def ready(self):
        return self.index.ntotal > 0

    @property
    def next_index(self) -> int:
        return self.index.ntotal
