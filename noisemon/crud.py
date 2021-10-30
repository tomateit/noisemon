from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
import models, schemas
from datetime import datetime
from functools import lru_cache
import numpy as np
# def get_entities(db: Session, Entity_id: int):
#     return db.query(models.Entity).filter(models.Entity.id == Entity_id).first()

##########
## ENTITY
##########
def get_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Entity).offset(skip).limit(limit).all()


def create_entity(db: Session, qid:str, entity_name: str, type: schemas.EntityType):
    db_Entity = models.Entity(name=entity_name, type=type, qid=qid)
    db.add(db_Entity)
    db.commit()
    db.refresh(db_Entity)
    return db_Entity

##########
## VECTOR
##########

def get_all_active_vectors(db: Session) -> List[np.ndarray]:
    query = select(models.VectorIndex.vector).where(models.VectorIndex.index > 0).order_by(models.VectorIndex.index.asc())
    query_result = db.execute(query).all()
    #!add consistency check - we do not know that vectors in db had indices like 0,1,2,3,4,5...
    query_result = map(lambda x: np.frombuffer(x[0], dtype="float32"), query_result)
    return list(query_result)
    

def create_vector_index(db: Session, entity_qid:str, index: int, span: str, source: str, vector: np.ndarray):
    db_VectorIndex = models.VectorIndex(
        index=index, 
        entity_qid=entity_qid, 
        span=span, 
        source=source,
        vector=vector,
        # created_at=datetime.now(),
    )
    db.add(db_VectorIndex)
    db.commit()
    db.refresh(db_VectorIndex)
    return db_VectorIndex

@lru_cache(maxsize=512)
def get_qid_by_vector_index(db: Session, index: int) -> Optional[str]:
    query_result = db.execute(select(models.VectorIndex.entity_qid).where(models.VectorIndex.index == index)).first()
    if query_result:
        return query_result[0]["qid"]
    else:
        return None

@lru_cache(maxsize=512)
def get_aliases_by_qid(db: Session, qid: int) -> List[str]:
    query_result = db.execute(select(models.VectorIndex.span).where(models.VectorIndex.entity_qid == qid).distinct()).all()
    return [record[0] for record in query_result]

##########
## MENTION
##########
def create_entity_mention(db: Session, entity_qid: str, timestamp: str, source: str):
    timestamp = datetime.fromisoformat(timestamp)
    db_Mention = models.Mention(entity_qid=entity_qid, timestamp=timestamp, source=source)
    db.add(db_Mention)
    db.commit()
    db.refresh(db_Mention)
    return db_Mention
    # mention_id = Column(String, name="qid", primary_key=True, default=generate_uuid)
    # source = Column(String)
    # timestamp = Column(TIMESTAMP)
    # entity_qid = Column(String, ForeignKey("entities.qid"))
    # entity = relationship("Entity", b


# def get_mentions(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()

