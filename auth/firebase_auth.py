import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import InvalidIdTokenError
from fastapi import HTTPException, Depends, Header
from typing import Optional, Dict

# Initialize Firebase Admin SDK
cred = credentials.Certificate("auth/drug-script-firebase-adminsdk-fbsvc-aa7980f96c.json")
firebase_admin.initialize_app(cred)

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
