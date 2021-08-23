from sqlalchemy.orm import Session
import models, schemas

# def get_entities(db: Session, Entity_id: int):
#     return db.query(models.Entity).filter(models.Entity.id == Entity_id).first()


# def get_Entity_by_email(db: Session, email: str):
#     return db.query(models.Entity).filter(models.Entity.email == email).first()


def get_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Entity).offset(skip).limit(limit).all()


def create_entity(db: Session, entity: str):
    db_Entity = models.Entity(name=entity, type=schemas.EntityType.ORGANIZATION)
    db.add(db_Entity)
    db.commit()
    db.refresh(db_Entity)
    return db_Entity


# def get_mentions(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()

