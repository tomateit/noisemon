from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
import numpy as np

# https://stackoverflow.com/questions/18621513/python-insert-numpy-array-into-sqlite3-database
def adapt_array(arr: np.ndarray):
    return arr.astype('float32').tobytes()

def convert_array(text):
    return np.frombuffer(text, dtype='float32')

sqlite3.register_adapter(np.array, adapt_array)    
sqlite3.register_converter("vector", convert_array)

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={
        "check_same_thread": False, 
        "detect_types": sqlite3.PARSE_DECLTYPES
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()