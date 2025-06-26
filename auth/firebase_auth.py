import os
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import InvalidIdTokenError
from fastapi import HTTPException, Depends, Header
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "auth/drug-script-firebase-adminsdk-fbsvc-aa7980f96c.json")

try:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Firebase: {e}")
    raise

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
