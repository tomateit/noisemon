from datetime import datetime
from fastapi import FastAPI

from models.response import Response


app = FastAPI()

@app.get("/", response_model=Response)
def index_page() -> Response:
    return {
        "timestamp": datetime.utcnow(),
    }


# @app.get("/", response_model=Response)
# def index_page() -> Response:
#     return {
#         "timestamp": datetime.utcnow(),
#     }
