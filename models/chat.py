from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    sender_id: str
    content: str

class MessageOut(BaseModel):
    id: str
    sender_id: str
    content: str
    timestamp: datetime