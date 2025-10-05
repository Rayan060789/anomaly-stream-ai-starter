
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Event(BaseModel):
    ts: datetime
    user_id: str
    metric1: float = Field(ge=0)
    metric2: float = Field(ge=0)
    metric3: float = Field(ge=0)
    feature_a: float = 0.0
    feature_b: float = 0.0
    tag: Optional[str] = None

class EventBatch(BaseModel):
    events: List[Event]
