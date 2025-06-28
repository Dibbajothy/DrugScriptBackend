from fastapi import APIRouter, status
from typing import List
from config.database import messages_collection
from datetime import datetime
from models.chat import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(message: MessageCreate):
    msg_doc = {
        "sender_id": message.sender_id,
        "content": message.content,
        "timestamp": datetime.utcnow()
    }
    result = messages_collection.insert_one(msg_doc)
    msg_doc["id"] = str(result.inserted_id)
    return {
        "id": msg_doc["id"],
        "sender_id": msg_doc["sender_id"],
        "content": msg_doc["content"],
        "timestamp": msg_doc["timestamp"]
    }

@router.get("/", response_model=List[MessageOut])
async def get_messages():
    messages = messages_collection.find().sort("timestamp", 1)
    return [
        {
            "id": str(msg["_id"]),
            "sender_id": msg["sender_id"],
            "content": msg["content"],
            "timestamp": msg["timestamp"]
        }
        for msg in messages
    ]