from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime
from bson.objectid import ObjectId

router = APIRouter()

class Prescription(BaseModel):
    doctor_name: str
    contact: str
    date: str  # Date in ISO format (DD-MM-YYYY)
    diagnosis: str
    medicines: list[dict]  # List of medicines with their details
    image: str  # Base64 encoded image string
    created_by: str  # Optional field to track who created the prescription

@router.post("/add_prescription")
async def add_prescription(prescription: Prescription, user_id: str = Depends(get_current_user)):
    try:
        # Use unified database connection
        prescriptions_collection = db["prescriptions"]
        
        # Create a document to insert into MongoDB
        prescription_doc = {
            "user_id": user_id,
            "doctor_name": prescription.doctor_name,
            "contact": prescription.contact,
            "date": prescription.date,  # Assuming date is in ISO format (DD-MM-YYYY)
            "diagnosis": prescription.diagnosis,
            "medicines": prescription.medicines,
            "image": prescription.image,
            "created_by": prescription.created_by,
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
            "date": prescription.date,
            "diagnosis": prescription.diagnosis,
            "medicines": prescription.medicines,
            "created_by": prescription.created_by,
            "created_at": prescription_doc["created_at"].strftime("%H:%M:%S"),
            "user_id": user_id
        }
    except Exception as e:
        print(f"Error adding prescription to MedicineAppDB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add prescription: {str(e)}"
        )

@router.get("/prescriptions")
async def get_prescriptions(user_id: str = Depends(get_current_user)):
    try:
        # Use unified database connection
        prescriptions_collection = db["prescriptions"]
        
        # Query prescriptions for the authenticated user and sort by created_at in descending order
        cursor = prescriptions_collection.find({"user_id": user_id}).sort("created_at", -1)
        
        # Convert MongoDB documents to a list of dictionaries with only the requested fields
        prescriptions = []
        for doc in cursor:
            # Extract only the needed fields
            prescription = {
                "prescription_id": str(doc["_id"]),
                "doctor_name": doc["doctor_name"],
                "date": doc["date"],
                "diagnosis": doc["diagnosis"],
                "created_at": doc["created_at"].isoformat() if "created_at" in doc else None
            }
            
            prescriptions.append(prescription)
        
        return {
            "prescriptions": prescriptions
        }
    except Exception as e:
        print(f"Error fetching prescriptions from MedicineAppDB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prescriptions: {str(e)}"
        )


@router.get("/prescription/{prescription_id}")
async def get_prescription_by_id(prescription_id: str, user_id: str = Depends(get_current_user)):
    try:
        # Use unified database connection
        prescriptions_collection = db["prescriptions"]
        
        # Query the specific prescription
        prescription = prescriptions_collection.find_one({
            "_id": ObjectId(prescription_id),
            "$or": [
                {"user_id": user_id},          # owner
                {"shared_with": user_id}       # has been shared with me
            ]  # Security check to ensure user only accesses their own prescriptions
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
        print(f"Error fetching prescription from MedicineAppDB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prescription: {str(e)}"
        )
    

    
@router.delete("/prescription/{prescription_id}")
async def delete_prescription(prescription_id: str, user_id: str = Depends(get_current_user)):
    try:
        # Use unified database connection
        prescriptions_collection = db["prescriptions"]
        
        # Delete the specific prescription
        result = prescriptions_collection.delete_one({
            "_id": ObjectId(prescription_id),
            "user_id": user_id  # Security check to ensure user only deletes their own prescriptions
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription not found or you do not have permission to delete it"
            )
        
        return {
            "message": "Prescription deleted successfully"
        }
    except Exception as e:
        print(f"Error deleting prescription from MedicineAppDB: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete prescription: {str(e)}"
        )