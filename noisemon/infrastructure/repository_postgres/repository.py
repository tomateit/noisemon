from noisemon.domain.services.repository.repository import Repository


class RepositoryPostgresImpl(Repository):
    def __init__(self, connection_string: str):


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


# def get_all_entities_qids(db: Session) -> List[str]:
#     query = select(EntityModel.qid)
#     result = db.execute(query).scalars().all()
#     db.commit()
#     return result


# def get_by_qid(db: Session, qid: str) -> Optional[EntityModel]:
#     query = (select(EntityModel).filter_by(qid=qid))
#     result = db.execute(query).scalars().first()
#     return result


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
