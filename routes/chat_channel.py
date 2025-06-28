from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from config.database import db, messages_collection
from bson import ObjectId
from datetime import datetime

channel_collection = db["channels"]

class ChannelCreate(BaseModel):
    name: str

class ChannelOut(BaseModel):
    id: str
    name: str

class MessageCreate(BaseModel):
    sender_id: str
    content: str

class MessageOut(BaseModel):
    id: str
    channel_id: str
    sender_id: str
    content: str
    timestamp: datetime

router = APIRouter(prefix="/channels", tags=["Chat Channels"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_channel(channel: ChannelCreate):
    if channel_collection.find_one({"name": channel.name}):
        raise HTTPException(status_code=400, detail="Channel already exists")
    result = channel_collection.insert_one(channel.dict())
    return {"id": str(result.inserted_id), "name": channel.name}

@router.get("/", response_model=List[ChannelOut])
async def list_channels():
    channels = channel_collection.find()
    return [
        {
            "id": str(channel["_id"]),
            "name": channel["name"]
        }
        for channel in channels
    ]

@router.delete("/{channel_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(channel_name: str):
    result = channel_collection.delete_one({"name": channel_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Channel not found")
    return

@router.post("/{channel_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def send_message(channel_id: str, message: MessageCreate):
    # Check if channel exists
    if not channel_collection.find_one({"_id": ObjectId(channel_id)}):
        raise HTTPException(status_code=404, detail="Channel not found")
    msg_doc = {
        "channel_id": channel_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "timestamp": datetime.utcnow()
    }
    result = messages_collection.insert_one(msg_doc)
    msg_doc["id"] = str(result.inserted_id)
    msg_doc["timestamp"] = msg_doc["timestamp"]
    return {
        "id": msg_doc["id"],
        "channel_id": msg_doc["channel_id"],
        "sender_id": msg_doc["sender_id"],
        "content": msg_doc["content"],
        "timestamp": msg_doc["timestamp"]
    }

@router.get("/{channel_id}/messages", response_model=List[MessageOut])
async def get_channel_messages(channel_id: str):
    # Check if channel exists
    if not channel_collection.find_one({"_id": ObjectId(channel_id)}):
        raise HTTPException(status_code=404, detail="Channel not found")
    messages = messages_collection.find({"channel_id": channel_id}).sort("timestamp", 1)
    return [
        {
            "id": str(msg["_id"]),
            "channel_id": msg["channel_id"],
            "sender_id": msg["sender_id"],
            "content": msg["content"],
            "timestamp": msg["timestamp"]
        }
        for msg in messages
    ]