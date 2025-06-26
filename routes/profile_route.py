from fastapi import APIRouter, Depends, HTTPException, status
from models.profile import Profile, ProfileCreate, ProfileUpdate
from config.database import profile_collection
from schema.schemas import profile_serializer
from bson import ObjectId
from auth.firebase_auth import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    responses={404: {"description": "Not found"}},
)

# Get user's profile
@router.get("", response_model=dict)  # Changed from Profile to dict
async def get_profile(user_id: str = Depends(get_current_user)):
    profile = profile_collection.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=404, 
            detail="Profile not found"
        )
    return profile_serializer(profile)

# Create user profile
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate, user_id: str = Depends(get_current_user)):
    # Check if profile already exists
    existing_profile = profile_collection.find_one({"user_id": user_id})
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists for this user"
        )
    
    # Create profile dictionary
    profile_dict = profile.dict()
    profile_dict["user_id"] = user_id
    
    # Insert into database
    result = profile_collection.insert_one(profile_dict)
    
    # Return created profile
    created_profile = profile_collection.find_one({"_id": result.inserted_id})
    return profile_serializer(created_profile)

# Update user profile
@router.put("", response_model=dict)  # Changed from Profile to dict
async def update_profile(profile: ProfileUpdate, user_id: str = Depends(get_current_user)):
    # Check if profile exists
    existing_profile = profile_collection.find_one({"user_id": user_id})
    if not existing_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    # Update only provided fields
    update_dict = profile.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )
    
    # Update profile
    profile_collection.update_one(
        {"user_id": user_id},
        {"$set": update_dict}
    )
    
    # Return updated profile
    updated_profile = profile_collection.find_one({"user_id": user_id})
    return profile_serializer(updated_profile)

# Delete user profile
@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(user_id: str = Depends(get_current_user)):
    # Check if profile exists
    existing_profile = profile_collection.find_one({"user_id": user_id})
    if not existing_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    # Delete profile
    profile_collection.delete_one({"user_id": user_id})
    return {"message": "Profile deleted successfully"}