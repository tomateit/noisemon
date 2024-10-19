from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from noisemon.infrastructure.repository_postgres.database_models import Base, EntityORMModel, DocumentORMModel, \
    MentionORMModel
from noisemon.settings import settings

url = settings.DATABASE_URI
if not database_exists(url):
    create_database(url)

engine = create_engine(url)
Base.metadata.create_all(engine)
print(Base)
