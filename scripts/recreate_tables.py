from sqlalchemy_utils import create_database, database_exists

from noisemon.database.database import *
from noisemon.models.mention import MentionModel
from noisemon.models.entity import  EntityModel
from noisemon.models.document import DocumentModel
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
