from fastapi import APIRouter, Depends
from pydantic import BaseModel
import routes.medicines.drug_fetch as drug_fetch  # Fixed import

router = APIRouter()


class SearchQuery(BaseModel):
    query: str


@router.post("/medicinesearch")
async def search(search_query: SearchQuery):
    results = drug_fetch.search_medicine(search_query.query)
    return {"results": results[:40]}


@router.get("/medicine/{medicine_id}")
async def get_medicine_details(medicine_id: str):
    # Connect to MongoDB if not already connected
    if drug_fetch.db is None:
        drug_fetch.connect_to_mongodb()
        
    # Find medicine directly in MongoDB
    medicine = drug_fetch.db["new_medicines"].find_one({"slug": medicine_id}, {'_id': 0})
    
    if medicine:
        # Clean the medicine data before returning
        return drug_fetch.clean_document(medicine)
    return {"error": "Medicine not found"}