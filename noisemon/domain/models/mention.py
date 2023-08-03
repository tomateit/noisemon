import uuid
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

import numpy as np
from noisemon.database.database import Base


def generate_uuid():
    return str(uuid.uuid4())

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
# class MentionModel(Base):
#     __tablename__ = "mentions"
#     mention_id = Column(String, name="id", primary_key=True, default=generate_uuid)
#     entity_qid = Column(String, ForeignKey("entities.qid"), name="entity_qid", nullable=False)
#     origin_id = Column(String, ForeignKey("documents.id"), name="origin_id", nullable=False)
#
#     entity = relationship("EntityModel", back_populates="mentions")
#     origin = relationship("DocumentModel", back_populates="mentions")
#
#     span = Column(String, name="span", nullable=False)  # textual form
#     span_start = Column(Integer, name="span_start", nullable=False)
#     span_end = Column(Integer, name="span_end", nullable=False)
#
#     vector_index = Column(Integer, name="vector_index", nullable=True, default=None)  # integer that match vector in faiss index
#     vector = Column(NumpyNDArrayFloat32AsBytes, name="vector", nullable=True)  # numpy (d,) vector as bytes "float32"
#     # metadata for analytics
#     created_at = Column(DateTime, default=datetime.now, nullable=True)
#     number_of_matches = Column(Integer, name="number_of_matches", default=0,
#                                nullable=False)  # how many times an entity was matched with this vector
#
#     def __repr__(self):
#         return f"Mention[span={self.span},qid={self.entity_qid}]"
#
#
# def get_all_active_vectors(db: Session) -> Optional[np.ndarray]:
#     """
#     Returns list of numpy vectors representing Mention.vector's of respective Vector Indices with 'index>=0', sorted in asc
#     Vectors with index<0 considered as deactivated
#     """
#     with db.begin():
#         query = select(MentionModel).where(MentionModel.vector_index >= 0).order_by(MentionModel.vector_index.asc())
#         query_result = db.execute(query).scalars().all()
#         # consistency check - vectors in db must have indices like 0,1,2,3,4,5... otherwise faiss indices will not map
#         list_of_retrieved_indices = sorted([int(x.vector_index) for x in query_result])
#         assert list_of_retrieved_indices == list(
#             range(len(query_result))), "Retrieved Mention indices must be consequential as 0...len(vecs)"
#
#         query_result = [x.vector for x in query_result]
#         if query_result:
#             return np.vstack(query_result)
#         else:
#             return None
#
#
#
# def get_by_vector_index(db: Session, index: int) -> Optional[MentionModel]:
#     if db.in_transaction():
#         db.commit()
#     with db.begin():
#         statement = (select(MentionModel)
#                      .filter_by(vector_index=index))
#         mention = db.execute(statement).scalars().first()
#     return mention
#
#
# def get_all_mentioned_qids(db: Session) -> List[str]:
#     query = select(MentionModel.entity_qid).distinct()
#     result = db.execute(query).scalars().all()
#     db.commit()
#     return result
#
#
# def increment_number_of_mentions(db: Session, mention_model: MentionModel):
#     with db.begin_nested():
#         mention_model.number_of_matches += 1
