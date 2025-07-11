from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class Recipient(BaseModel):
    user_id: str
    name: Optional[str]

class SentPrescriptionOut(BaseModel):
    prescription_id: str
    doctor_name: Optional[str]
    date: Optional[str]
    diagnosis: Optional[str]
    created_at: Optional[datetime]
    recipients: List[Recipient]

@router.get(
    "/sentPrescriptions",
    response_model=List[SentPrescriptionOut],
    summary="List all of the current user's prescriptions that have been shared, with their recipients"
)
async def list_sent_prescriptions(
    user_id: str = Depends(get_current_user)
) -> List[SentPrescriptionOut]:
    pres_coll = db["prescriptions"]
    prof_coll = db["profiles"]

    # Find all my prescriptions that have at least one share
    cursor = pres_coll.find({
        "user_id": user_id,
        "shared_with": {"$exists": True, "$ne": []}
    })

    out: List[SentPrescriptionOut] = []
    # Use a regular (synchronous) for-loop over the cursor
    for pres in cursor:
        recips: List[Recipient] = []
        for uid in pres.get("shared_with", []):
            profile = prof_coll.find_one({"user_id": uid}) or {}
            recips.append(Recipient(
                user_id=uid,
                name=profile.get("name")
            ))

        out.append(SentPrescriptionOut(
            prescription_id=str(pres["_id"]),
            doctor_name   = pres.get("doctor_name"),
            date          = pres.get("date"),
            diagnosis     = pres.get("diagnosis"),
            created_at    = pres.get("created_at"),
            recipients    = recips,
        ))

    return out
