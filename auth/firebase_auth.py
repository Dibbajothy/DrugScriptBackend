import os
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import InvalidIdTokenError
from fastapi import HTTPException, Depends, Header
from typing import Optional, Dict
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK


def initialize_firebase():
    try:
        # Check if running on Railway (production)
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            print("🚂 Running on Railway - using environment variables")

            # Get Firebase config from environment variables
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("FIREBASE_PRIVATE_KEY") else None,
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
                "universe_domain": "googleapis.com"
            }

            # Validate required fields
            required_fields = ["project_id", "private_key", "client_email"]
            missing_fields = [
                field for field in required_fields if not firebase_config.get(field)]

            if missing_fields:
                raise ValueError(
                    f"Missing Firebase environment variables: {missing_fields}")

            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized from Railway environment variables")

        else:
            # Local development - use JSON file
            print("💻 Running locally - using Firebase JSON file")
            firebase_credentials_path = os.getenv(
                "FIREBASE_CREDENTIALS_PATH", "auth/drug-script-firebase-adminsdk-fbsvc-aa7980f96c.json")

            if os.path.exists(firebase_credentials_path):
                cred = credentials.Certificate(firebase_credentials_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin SDK initialized from local JSON file")
            else:
                raise FileNotFoundError(
                    f"Firebase credentials file not found at {firebase_credentials_path}")

    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise


# Initialize Firebase when module is imported
initialize_firebase()


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        return user_id
    except InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )
    

async def get_current_user_with_username(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        email = decoded_token.get('name', '')
        return {"uid": user_id, "name": email}
    except InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )


async def get_current_user_with_email(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        email = decoded_token.get('email', '')
        return {"user_id": user_id, "email": email}
    except InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )


async def get_google_user_info(access_token: str) -> Dict[str, str]:
    """Fetch user information from Google API"""
    try:
        response = requests.get(
            f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        print(f"Error fetching Google user info: {e}")
        return {}


async def get_current_user_auto_register(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    """Get current user and auto-register if new user"""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        
        # Import here to avoid circular imports
        from config.database import profile_collection
        
        # Check if user profile exists
        existing_profile = profile_collection.find_one({"user_id": user_id})
        
        if not existing_profile:
            # Auto-create profile for new user
            profile_dict = {
                "user_id": user_id,
                "email": email,
                "name": name or email.split('@')[0],  # Use email prefix if no name
                "age": None,
                "address": None,
                "gender": None,
                "phone": None,
                "date_of_birth": None,
                "blood_type": None,
                "allergies": None,
                "medical_conditions": None,
                "emergency_contact": None
            }
            
            # Insert new profile
            profile_collection.insert_one(profile_dict)
            print(f"✅ Auto-created profile for new user: {email}")
        
        return {"user_id": user_id, "email": email, "name": name}
        
    except InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )
