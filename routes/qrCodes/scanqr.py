from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class PrescriptionIn(BaseModel):
    prescription_id: str

@router.post("/recievedPrescription")
async def receive_prescription(
    data: PrescriptionIn,
    user_id: str = Depends(get_current_user),
):
    rec_coll  = db["recieved_prescription"]
    pres_coll = db["prescriptions"]
    now       = datetime.utcnow()

    try:
        # 1) Upsert into recieved_prescription
        result = rec_coll.update_one(
            {"user_id": user_id},
            {
                "$setOnInsert": {
                    "created_at": now,
                    "user_id": user_id,
                },
                "$set": {"updated_at": now},
                "$addToSet": {"prescription_id": data.prescription_id},
            },
            upsert=True,
        )

        # 2) Also tag the original prescription itself
        #    by adding this user to its `shared_with` array
        pres_coll.update_one(
            {"_id": ObjectId(data.prescription_id)},
            {"$addToSet": {"shared_with": user_id}}
        )

        # 3) Return the usual response
        if result.upserted_id:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Prescription list created",
                    "id": str(result.upserted_id),
                },
            )
        if result.modified_count > 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Prescription code added"},
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Prescription code already exists"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}"
        )
