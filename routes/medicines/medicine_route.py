from fastapi import APIRouter
from pydantic import BaseModel
import routes.medicines.drug_fetch as drug_fetch
from config.database import db


router = APIRouter()


class SearchQuery(BaseModel):
    query: str


@router.post("/medicinesearch")
async def search(search_query: SearchQuery):
    results = drug_fetch.search_medicine(search_query.query)
    return {"results": results[:40]}


@router.get("/medicine/{medicine_id}")
async def get_medicine_details(medicine_id: str):
    # Use unified database connection
    medicine = db["medicines"].find_one({"slug": medicine_id}, {'_id': 0})
    
    if medicine:
        return drug_fetch.clean_document(medicine)
    return {"error": "Medicine not found"}