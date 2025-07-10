from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
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

class ReviewCreate(BaseModel):
    subject_id: str                     # clinicId or doctorId
    is_doctor: bool
    rating: int = Field(..., ge=1, le=5)
    review: str

class ReviewModel(ReviewCreate):
    id: str
    user_id: str
    user_name: str
    created_at: datetime

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



@router.get("/clinics/_search", response_model=List[ClinicModel])
async def search_clinics(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    try:
        regex   = {"$regex": q, "$options": "i"}
        cursor  = db.clinics.find({"Name": regex}).limit(limit)
        results = []
        for doc in cursor:
            results.append({
                "id":       str(doc.get("Id", "")),          # safe
                "name":     doc.get("Name", ""),
                "code":     str(doc.get("Code", "")),        # safe
                "district": doc.get("District", "")
            })
        return results
    except Exception as e:
        print("🔴 /clinics/search failed:", repr(e))
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    

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
    



# ——— Post a review ———
@router.post("/reviews", response_model=ReviewModel, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        doc = {
            "subject_id": payload.subject_id,
            "is_doctor": payload.is_doctor,
            "rating": payload.rating,
            "review": payload.review,
            "user_id": current_user["uid"],
            "user_name": current_user.get("name", "Anonymous"),
            "created_at": datetime.utcnow()
        }
        res = db.reviews.insert_one(doc)
        doc["id"] = str(res.inserted_id)
        return doc
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ——— Get reviews for a clinic or doctor ———
@router.get("/reviews", response_model=List[ReviewModel])
async def get_reviews(
    subject_id: str = Query(...),
    is_doctor: bool = Query(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        cursor = db.reviews.find({
            "subject_id": subject_id,
            "is_doctor": is_doctor
        }).sort("created_at", -1)
        out = []
        for r in cursor:
            out.append({
                "id": str(r["_id"]),
                "subject_id": r["subject_id"],
                "is_doctor": r["is_doctor"],
                "rating": r["rating"],
                "review": r["review"],
                "user_id": r["user_id"],
                "user_name": r["user_name"],
                "created_at": r["created_at"]
            })
        return out
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))