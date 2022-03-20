import sys
sys.path.append("noisemon")

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists   

from noisemon.database import *
from noisemon.models import Mention, Entity, Document
from noisemon.settings import settings
from noisemon.database import SessionLocal


url = settings.DATABASE_URI
if not database_exists(url):
    create_database(url)

engine = create_engine(url)
Base.metadata.create_all(engine)
Entity.__table__.create(engine)
Document.__table__.create(engine)
Mention.__table__.create(engine)
print(Base)