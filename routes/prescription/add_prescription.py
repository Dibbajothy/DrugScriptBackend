from urllib.parse import quote_plus
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from auth.firebase_auth import get_current_user


router = APIRouter()


# MongoDB connection
client = None
db = None

def connect_to_mongodb():

    global client, db
    try:
        password = quote_plus("hello@boy")
        client = MongoClient(f"mongodb+srv://dibbajothy2:{password}@tryout.fwsnut6.mongodb.net/?retryWrites=true&w=majority&appName=TryOut")
        db = client["PrescriptionDB"]
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise



class Prescription(BaseModel):
    doctor_name: str
    contact: str
    medicines: list[dict]  # List of medicines with their details
    image : str # Base64 encoded image string


@router.post("/add_prescription")
async def add_prescription(prescription: Prescription, user_id: str = Depends(get_current_user)):
    return {
        "message": "Prescription added successfully",
        "prescription": prescription,
        "medicines": prescription.medicines,
        "doctor_name": prescription.doctor_name,
        "contact": prescription.contact,
        "image": prescription.image,
        "user_id": user_id
    }