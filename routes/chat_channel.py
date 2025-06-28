from fastapi import APIRouter, HTTPException, status
from typing import List
from config.database import db, messages_collection
from bson import ObjectId
from datetime import datetime
from models.chat import ChannelCreate, ChannelOut, MessageCreate, MessageOut

channel_collection = db["channels"]

router = APIRouter(prefix="/channels", tags=["Chat Channels"])

# Ensure default general channel exists
def ensure_general_channel():
    general = channel_collection.find_one({"name": "general"})
    if not general:
        channel_collection.insert_one({
            "name": "general",
            "owner_id": None  # No owner for general channel
        })

ensure_general_channel()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_channel(channel: ChannelCreate):
    # ChannelCreate should have: name: str, owner_id: str
    if channel_collection.find_one({"name": channel.name, "owner_id": channel.owner_id}):
        raise HTTPException(status_code=400, detail="Channel already exists for this user")
    result = channel_collection.insert_one({
        "name": channel.name,
        "owner_id": channel.owner_id
    })
    return {"id": str(result.inserted_id), "name": channel.name, "owner_id": channel.owner_id}

@router.get("/", response_model=List[ChannelOut])
async def list_channels():
    channels = channel_collection.find()
    return [
        {
            "id": str(channel["_id"]),
            "name": channel["name"],
            "owner_id": channel.get("owner_id")
        }
        for channel in channels
    ]

@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(channel_id: str, owner_id: str):
    result = channel_collection.delete_one({"_id": ObjectId(channel_id), "owner_id": owner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Channel not found or not owned by user")
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