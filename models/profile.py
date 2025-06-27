from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class ProfileBase(BaseModel):
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[str] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class Profile(ProfileBase):
    id: str
    user_id: str
    email: str  # Gmail from Firebase auth
    
    class Config:
        from_attributes = True