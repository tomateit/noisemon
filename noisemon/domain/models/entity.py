from dataclasses import dataclass
from typing import Optional

# def generate_uuid():
#     return str(uuid.uuid4())
#

@dataclass(kw_only=True)
class EntityData:
    qid: str


# class EntityModel(Base):
#     __tablename__ = "entities"
#     qid = Column(String, name="qid", primary_key=True)
#     name = Column(String, unique=False, nullable=False)
#     type = Column(Enum(EntityType), nullable=True)
#
#     mentions = relationship("MentionModel", back_populates="entity", cascade="all,delete")
#
#     def __repr__(self):
#         return f"EntityModel[name={self.name},qid={self.qid}]"
#
#     @property
#     def aliases(self) -> Set[str]:
#         return set([x.span for x in self.mentions])


# def dataclass_to_model(o: EntityData) -> EntityModel:
#     return EntityModel(
#         qid=o.qid,
#         name=o.name,
#         type=o.type
#     )

# def get_all_entities_qids(db: Session) -> List[str]:
#     query = select(EntityModel.qid)
#     result = db.execute(query).scalars().all()
#     db.commit()
#     return result


# def get_by_qid(db: Session, qid: str) -> Optional[EntityModel]:
#     query = (select(EntityModel).filter_by(qid=qid))
#     result = db.execute(query).scalars().first()
#     return result

#
# def dataclass_to_dict(o: EntityData) -> dict:
#     return dict(
#         qid=o.qid,
#         name=o.name,
#         type=o.type
#     )

# def model_to_dict(o: EntityModel) -> dict:
#     return dict(
#         qid=o.qid,
#         name=o.name,
#         type=o.type
#     )
#
# def get_insert_statement(entity: EntityModel):
#     data = model_to_dict(entity)
#     return insert(EntityModel.__table__).values(**data).on_conflict_do_nothing(index_elements=["qid"])
#
# def get_insert_many_statement(entities: list[EntityModel]):
#     data = [model_to_dict(entity) for entity in entities]
#     return insert(EntityModel.__table__).values(data).on_conflict_do_nothing(index_elements=["qid"])
#
# def upsert_entity(db: Session, qid: str, name: str, type: Optional[EntityType]) -> EntityModel:
#     with db.begin():
#         query = (select(EntityModel).filter_by(qid=qid))
#         result = db.execute(query).scalars().first()
#         if result:
#             return result
#
#         entity = EntityModel(name=name, type=type, qid=qid)
#         db.add(entity)
#     return entity
#
#
# def get_entities(db: Session, skip: int = 0, limit: int = 100) -> List[EntityModel]:
#     return db.query(EntityModel).offset(skip).limit(limit).all()
