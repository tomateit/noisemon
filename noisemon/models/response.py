from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import datetime


class Response(BaseModel):
    timestamp: datetime


