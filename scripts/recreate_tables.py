from noisemon.database.database import *
from noisemon.domain.models.mention import MentionModel
from noisemon.domain.models.entity import  EntityModel
from noisemon.domain.models.document import DocumentModel
from noisemon.settings import settings

url = settings.DATABASE_URI
# if not database_exists(url):
#     create_database(url)

engine = create_engine(url)
Base.metadata.create_all(engine)
EntityModel.__table__.create(engine)
DocumentModel.__table__.create(engine)
MentionModel.__table__.create(engine)
print(Base)
