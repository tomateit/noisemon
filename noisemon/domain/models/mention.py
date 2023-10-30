import uuid
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

import numpy as np




#
# class NumpyNDArrayFloat32AsBytes(TypeDecorator):
#     impl = BYTEA
#     cache_ok = True
#
#     def process_bind_param(self, value, dialect):
#         if value is not None:
#             shape = value.shape
#             value = value.astype(np.float32).reshape((max(shape),)).tobytes()
#         return value
#
#     def process_result_value(self, value, dialect):
#         if value is not None:
#             value = np.frombuffer(value, np.float32)
#             shape = value.shape
#             value = value.reshape((max(shape),))
#         return value


@dataclass(kw_only=True)
class MentionData:
    mention_id: str
    entity_qid: str
    origin_id: str

    span: str
    span_start: str
    span_end: str

    vector_index: Optional[int]
    vector: Optional[np.ndarray]

    created_at: Optional[datetime]
    number_of_matches: int = 0

#
