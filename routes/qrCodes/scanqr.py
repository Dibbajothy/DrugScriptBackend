from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime
from bson.objectid import ObjectId

router = APIRouter()

class PrescriptionIn(BaseModel):
    prescription_id: str

@router.post(
    "/recievedPrescription",
    status_code=status.HTTP_201_CREATED,
    summary="Record a received prescription code for the current user",
)
async def receive_prescription(
    data: PrescriptionIn,
    user_id: str = Depends(get_current_user),
):
    """
    If a document for this user already exists in the 'recieved_prescription' collection,
    push the new code onto its `codes` array; otherwise create a new document.
    """
    coll = db["recieved_prescription"]
    try:
        # Try to find an existing document for this user
        existing = coll.find_one({"user_id": user_id})
        if existing:
            update_result = coll.update_one(
                {"user_id": user_id},
                {
                    "$push": {"prescription_id": data.prescription_id},
                    "$set": {"updated_at": datetime.utcnow()},
                }
            )
            return {
                "message": "Prescription code added",
                "modified_count": update_result.modified_count
            }
        else:
            # No document yet for this user: create one
            doc = {
                "user_id": user_id,
                "prescription_id": [data.prescription_id],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            insert_result = coll.insert_one(doc)
            return {
                "message": "Prescription list created",
                "id": str(insert_result.inserted_id)
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}"
        )
