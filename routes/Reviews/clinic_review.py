from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from auth.firebase_auth import get_current_user
from config.database import db
from datetime import datetime
from bson.objectid import ObjectId
from typing import List, Optional

router = APIRouter()

class ClinicModel(BaseModel):
    id: str
    name: str
    code: str
    district: str
    
    class Config:
        orm_mode = True

@router.get("/clinics", response_model=List[ClinicModel])
async def get_all_clinics(current_user: dict = Depends(get_current_user)):
    try:
        clinics = []
        cursor = db.clinics.find({})
        for doc in cursor:
            clinics.append({
                "id": str(doc.get("Id")),
                "name": doc.get("Name"),
                "code": str(doc.get("Code")),
                "district": doc.get("District")
            })
        return clinics
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/clinics/{clinic_id}", response_model=ClinicModel)
async def get_clinic_by_id(clinic_id: str, current_user: dict = Depends(get_current_user)):
    try:
        clinic = db.clinics.find_one({"Id": int(clinic_id)})
        if clinic:
            return {
                "id": str(clinic.get("Id")),
                "name": clinic.get("Name"),
                "code": str(clinic.get("Code")),
                "district": clinic.get("District")
            }
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinic not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
