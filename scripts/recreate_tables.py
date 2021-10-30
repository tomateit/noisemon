import sys
sys.path.append("noisemon")
from noisemon.models import *

from noisemon.database import SessionLocal
from sqlalchemy import create_engine

engine = create_engine("sqlite:///sqlite.db")
Base.metadata.create_all(engine)

