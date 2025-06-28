from fastapi import APIRouter, Depends, HTTPException, status
from models.profile import Profile, ProfileCreate, ProfileUpdate
from config.database import profile_collection
from schema.schemas import profile_serializer
from bson import ObjectId
from auth.firebase_auth import get_current_user, get_current_user_with_email, get_current_user_auto_register
from typing import Dict

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    responses={404: {"description": "Not found"}},
)

# Auto-register and get user profile (main endpoint for login)
@router.post("/auth-login", response_model=dict)
async def auth_login(user_data: Dict[str, str] = Depends(get_current_user_auto_register)):
    """Auto-register user if new, then return profile"""
    user_id = user_data["user_id"]
    
    # Get the profile (should exist now due to auto-registration)
    profile = profile_collection.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=500,
            detail="Failed to create or retrieve user profile"
        )
    
    return {
        "message": "Login successful",
        "profile": profile_serializer(profile),
        "is_new_user": True if not profile.get("phone") else False  # Basic check for completed profile
    }

# Get user's profile
@router.get("", response_model=dict)
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
async def create_profile(
    profile: ProfileCreate, 
    user_data: Dict[str, str] = Depends(get_current_user_with_email)
):
    user_id = user_data["user_id"]
    email = user_data["email"]
    
    # Check if profile already exists
    existing_profile = profile_collection.find_one({"user_id": user_id})
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists for this user"
        )
    
    # Validate age if provided
    if profile.age is not None and (profile.age < 0 or profile.age > 150):
        raise HTTPException(
            status_code=400,
            detail="Invalid age. Age must be between 0 and 150."
        )
    
    # Create profile dictionary
    profile_dict = profile.model_dump()
    profile_dict["user_id"] = user_id
    profile_dict["email"] = email
    
    # Insert into database
    result = profile_collection.insert_one(profile_dict)
    
    # Return created profile
    created_profile = profile_collection.find_one({"_id": result.inserted_id})
    return profile_serializer(created_profile)

# Update user profile
@router.put("", response_model=dict)
async def update_profile(profile: ProfileUpdate, user_id: str = Depends(get_current_user)):
    # Check if profile exists
    existing_profile = profile_collection.find_one({"user_id": user_id})
    if not existing_profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    # Update only provided fields
    update_dict = profile.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )
    
    # Validate age if provided
    if "age" in update_dict and update_dict["age"] is not None and (update_dict["age"] < 0 or update_dict["age"] > 150):
        raise HTTPException(
            status_code=400,
            detail="Invalid age. Age must be between 0 and 150."
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

# Get profile by email (for admin purposes)
@router.get("/by-email/{email}")
async def get_profile_by_email(email: str, user_id: str = Depends(get_current_user)):
    profile = profile_collection.find_one({"email": email})
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found for this email"
        )
    return profile_serializer(profile)

@router.get("/public/{user_id}", response_model=dict)
async def get_public_profile(user_id: str):
    profile = profile_collection.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_serializer(profile)