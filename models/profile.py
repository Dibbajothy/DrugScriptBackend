from pydantic import BaseModel
from typing import Optional

class ProfileBase(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_type: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_type: Optional[str] = None

class Profile(ProfileBase):
    id: str
    user_id: str
    
    class Config:
        from_attributes = True  # Updated for Pydantic v2