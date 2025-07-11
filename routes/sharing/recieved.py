from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter()

class ReceivedPrescriptionOut(BaseModel):
    prescription_id: str
    doctor_name: Optional[str]
    date: Optional[str]
    diagnosis: Optional[str]
    created_at: Optional[datetime]
    owner_name: Optional[str]

@router.get(
    "/recievedPrescription",
    response_model=List[ReceivedPrescriptionOut],
    summary="List all prescriptions this user has received",
)
async def list_received_prescriptions(
    user_id: str = Depends(get_current_user)
) -> List[ReceivedPrescriptionOut]:
    rec_doc = db["recieved_prescription"].find_one({"user_id": user_id})
    if not rec_doc:
        return []

    pres_coll = db["prescriptions"]
    prof_coll = db["profiles"]
    out: List[ReceivedPrescriptionOut] = []

    for pid_str in rec_doc.get("prescription_id", []):
        try:
            pid = ObjectId(pid_str)
        except:
            continue

        pres = pres_coll.find_one({"_id": pid})
        if not pres:
            continue

        profile    = prof_coll.find_one({"user_id": pres.get("user_id")}) or {}
        owner_name = profile.get("name", "")

        out.append(ReceivedPrescriptionOut(
            prescription_id=str(pres["_id"]),
            doctor_name   = pres.get("doctor_name"),
            date          = pres.get("date"),
            diagnosis     = pres.get("diagnosis"),
            created_at    = pres.get("created_at"),
            owner_name    = owner_name,
        ))

    return out
