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

    # 1) find all prescriptions owned by me that have a non-empty shared_with array
    cursor = pres_coll.find({
        "user_id": user_id,
        "shared_with": {"$exists": True, "$ne": []}
    })

    out: List[SentPrescriptionOut] = []
    async for pres in cursor:  # if your driver supports async; otherwise use a sync loop
        # 2) build recipient list
        recips = []
        for uid in pres.get("shared_with", []):
            profile = prof_coll.find_one({"user_id": uid}) or {}
            recips.append(Recipient(
                user_id=uid,
                name=profile.get("name", "")
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
