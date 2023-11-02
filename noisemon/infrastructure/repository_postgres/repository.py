import sqlalchemy
from sqlalchemy import create_engine, select, distinct
from sqlalchemy.orm import sessionmaker

from noisemon.domain.services.repository.repository import Repository
from noisemon.infrastructure.repository_postgres.database_models import EntityModel
from .database_models import *
from ...domain.models.mention import PersistedMentionData, MentionData


class RepositoryPostgresImpl(Repository):
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_entity_by_qid(self, entity_qid: str) -> EntityData | None:
        entity = self.session.get(EntityModel, entity_qid)
        if entity is not None:
            entity = entity_model_to_dataclass(entity)
        return entity

    def get_document_by_id(self, document_id: str) -> PersistedDocumentData | None:
        document = self.session.get(DocumentModel, document_id)
        if document is not None:
            document = document_model_to_dataclass(document)
        return document

    def get_mention_by_id(self, mention_id: str) -> PersistedMentionData | None:
        mention = self.session.get(MentionModel, mention_id)
        if mention is not None:
            mention = mention_model_to_dataclass(mention)
        return mention


    def get_similar_mentions(self, mention: MentionData, max_mentions: int = 20) -> list[PersistedMentionData]:
        statement = (
            select(MentionModel)
            .order_by(MentionModel.vector.max_inner_product(mention.vector))
            .limit(max_mentions)
        )
        with self.session.begin_nested():
            mentions = self.session.scalars(statement).all()
        mentions = [mention_model_to_dataclass(m) for m in mentions]
        return mentions

    def get_entity_aliases_by_qid(self, qid: EntityQID) -> list[str]:
        statement = select(distinct(MentionModel.span)).filter_by(entity_qid=qid)
        results = self.session.scalars(statement).all()
        results = [str(r) for r in results] # does not seem necessary
        return results


    def persist_new_document(self, document: DocumentData) -> PersistedDocumentData:
        new_document_model = document_dataclass_to_model(document)
        with self.session.begin_nested():
            self.session.add(new_document_model)
        self.session.commit()
        result = document_model_to_dataclass(new_document_model)
        return result

    def persist_new_mention(self, mention: MentionData, document: PersistedDocumentData) -> PersistedMentionData:
        assert document.document_id is not None, "Only persisted documents are acceptable"
        if mention.document_id != document.document_id:
            raise ValueError("Document ID do not match")

        if mention.document_id is None:
            mention.document_id = document.document_id

        new_mention = mention_dataclass_to_model(mention)
        with self.session.begin_nested():
            self.session.add(new_mention)
        self.session.commit()
        result = mention_dataclass_to_model(new_mention)
        return result

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
