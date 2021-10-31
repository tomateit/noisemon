from typing import Optional, List
from datetime import datetime
from functools import lru_cache

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Entity, VectorIndex, Mention
import schemas
# def get_entities(db: Session, Entity_id: int):
#     return db.query(models.Entity).filter(models.Entity.id == Entity_id).first()

##########
## ENTITY
##########
def get_entities(db: Session, skip: int = 0, limit: int = 100) -> List[Entity]:
    return db.query(Entity).offset(skip).limit(limit).all()

def get_all_entity_qids(db: Session) -> List[str]:
    query = select(Entity.qid)
    result = db.execute(query).scalars().all()
    db.commit()
    return result

def create_entity(db: Session, qid:str, entity_name: str, type: schemas.EntityType) -> Entity:
    with db.begin():
        entity = Entity(name=entity_name, type=type, qid=qid)
        db.add(entity)
    return entity

##########
## VECTOR
##########

def get_all_active_vectors(db: Session) -> List[np.ndarray]:
    """
    Returns list of numpy vectors representing VectorIndex.vector's of respective Vector Indices with 'index>=0', sorted in asc
    """
    with db.begin():
        query = select(VectorIndex).where(VectorIndex.index >= 0).order_by(VectorIndex.index.asc())
        query_result = db.execute(query).scalars().all()
        # consistency check - vectors in db must have indices like 0,1,2,3,4,5... otherwise faiss indices will not map
        list_of_retrieved_indices = sorted([int(x.index) for x in query_result])
        assert list_of_retrieved_indices == list(range(len(query_result))), "Retrieved VectorIndex indices must be consequential as 0...len(vecs)"

        query_result = map(lambda x: np.frombuffer(x.vector, dtype="float32"), query_result)
        # db.commit()
    return list(query_result)
    

def get_vector_index_by_index(db: Session, index: int) -> Optional[VectorIndex]:
    db.commit()
    with db.begin():
        statement = (select(VectorIndex)
            .filter_by(index=index))
        vector_index = db.execute(statement).scalars().first()
    return vector_index

def get_all_vector_index_qids(db: Session) -> List[str]:
    query = select(VectorIndex.entity_qid).distinct()
    result = db.execute(query).scalars().all()
    db.commit()
    return result

def create_vector_index(db: Session, entity_qid:str, index: int, span: str, source: str, vector: np.ndarray) -> VectorIndex:
    with db.begin():
        vector_index = VectorIndex(
            index=index, 
            entity_qid=entity_qid, 
            vector=vector,
            span=span, 
            source=source,
        )
        db.add(vector_index)
        db.commit()
    return vector_index

def increment_number_of_mentions(db: Session, vector_index: VectorIndex):
    with db.begin():
        vector_index.number_of_matches += 1

# @lru_cache(maxsize=512)
# def get_aliases_by_qid(db: Session, qid: int) -> List[str]:
#     statement = select(models.VectorIndex.span)
#         .filter_by(entity_qid = qid)
#         .distinct()
        
#     query_result = db.execute(statement).scalars().all()
#     return query_result
    # return [record[0] for record in query_result]


##########
## MENTION
##########
def create_entity_mention(db: Session, entity: Entity, timestamp: str, source: str):
    with db.begin():
        timestamp = datetime.fromisoformat(timestamp)
        mention = Mention(
            entity_qid=Entity.qid, 
            timestamp=timestamp, 
            source=source
        )
        db.add(mention)
    return mention
    


