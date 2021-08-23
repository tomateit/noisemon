from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=schemas.Response)
def index_page() -> schemas.Response:
    return {
        "timestamp": datetime.utcnow(),
    }

@app.get("/entities/", response_model=List[schemas.Entity])
def read_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entities = crud.get_entities(db, skip=skip, limit=limit)
    return entities

# @app.get("/", response_model=Response)
# def index_page() -> Response:
#     return {
#         "timestamp": datetime.utcnow(),
#     }
