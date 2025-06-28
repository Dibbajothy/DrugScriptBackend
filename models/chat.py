from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChannelCreate(BaseModel):
    name: str
    owner_id: Optional[str] = None

class ChannelOut(BaseModel):
    id: str
    name: str
    owner_id: Optional[str] = None

class MessageCreate(BaseModel):
    sender_id: str
    content: str

class MessageOut(BaseModel):
    id: str
    channel_id: str
    sender_id: str
    content: str
    timestamp: datetime