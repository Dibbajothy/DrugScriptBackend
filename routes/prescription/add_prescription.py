from urllib.parse import quote_plus
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from pymongo import MongoClient
from auth.firebase_auth import get_current_user
from datetime import datetime


router = APIRouter()


# MongoDB connection
client = None
db = None
prescriptions_collection = None

def connect_to_mongodb():
    global client, db, prescriptions_collection
    try:
        password = quote_plus("hello@boy")
        client = MongoClient(f"mongodb+srv://dibbajothy2:{password}@tryout.fwsnut6.mongodb.net/?retryWrites=true&w=majority&appName=TryOut")
        db = client["PrescriptionDB"]
        prescriptions_collection = db["prescriptions"]
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


# Connect to MongoDB when module is imported
connect_to_mongodb()


class Prescription(BaseModel):
    doctor_name: str
    contact: str
    medicines: list[str]  # List of medicines with their details
    image: str  # Base64 encoded image string


@router.post("/add_prescription")
async def add_prescription(prescription: Prescription, user_id: str = Depends(get_current_user)):
    try:
        # Create a document to insert into MongoDB
        prescription_doc = {
            "user_id": user_id,
            "doctor_name": prescription.doctor_name,
            "contact": prescription.contact,
            "medicines": prescription.medicines,
            "image": prescription.image,
            "created_at": datetime.utcnow()
        }
        
        # Insert the document
        result = prescriptions_collection.insert_one(prescription_doc)
        
        # Return success response with the ID of the inserted document
        return {
            "message": "Prescription added successfully",
            "prescription_id": str(result.inserted_id),
            "doctor_name": prescription.doctor_name,
            "contact": prescription.contact,
            "medicines": prescription.medicines,
            "user_id": user_id
        }
    except Exception as e:
        # Log the error
        print(f"Error adding prescription to MongoDB: {e}")
        # Raise an HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add prescription: {str(e)}"
        )


@router.get("/prescriptions")
async def get_prescriptions(user_id: str = Depends(get_current_user)):
    try:
        # Query prescriptions for the authenticated user
        cursor = prescriptions_collection.find({"user_id": user_id})
        
        # Convert MongoDB documents to a list of dictionaries
        prescriptions = []
        for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            doc["_id"] = str(doc["_id"])
            # Convert datetime to string for JSON serialization
            if "created_at" in doc:
                doc["created_at"] = doc["created_at"].isoformat()
            
            # Optionally omit the image field to reduce response size
            # doc.pop("image", None)
            
            prescriptions.append(doc)
        
        return {
            "prescriptions": prescriptions,
            "count": len(prescriptions)
        }
    except Exception as e:
        print(f"Error fetching prescriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prescriptions: {str(e)}"
        )


@router.get("/prescription/{prescription_id}")
async def get_prescription_by_id(prescription_id: str, user_id: str = Depends(get_current_user)):
    try:
        from bson.objectid import ObjectId
        
        # Query the specific prescription
        prescription = prescriptions_collection.find_one({
            "_id": ObjectId(prescription_id),
            "user_id": user_id  # Security check to ensure user only accesses their own prescriptions
        })
        
        if not prescription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription not found"
            )
        
        # Convert ObjectId to string
        prescription["_id"] = str(prescription["_id"])
        # Convert datetime to string
        if "created_at" in prescription:
            prescription["created_at"] = prescription["created_at"].isoformat()
        
        return prescription
    except Exception as e:
        print(f"Error fetching prescription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prescription: {str(e)}"
        )