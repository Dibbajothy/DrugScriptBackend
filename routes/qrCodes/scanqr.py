from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime

router = APIRouter()

class PrescriptionIn(BaseModel):
    prescription_id: str

@router.post("/recievedPrescription")
async def receive_prescription(
    data: PrescriptionIn,
    user_id: str = Depends(get_current_user),
):
    coll = db["recieved_prescription"]
    now = datetime.utcnow()

    try:
        result = coll.update_one(
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

        # 1) New document created
        if result.upserted_id:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Prescription list created",
                    "id": str(result.upserted_id),
                },
            )

        # 2) Array was modified (code added)
        if result.modified_count > 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Prescription code added"},
            )

        # 3) No modification => duplicate code
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Prescription code already exists"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {e}"
        )
