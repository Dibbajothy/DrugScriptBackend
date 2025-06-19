import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import InvalidIdTokenError
from fastapi import HTTPException, Depends, Header
from typing import Optional

# Initialize Firebase Admin SDK
cred = credentials.Certificate("auth/drug-script-firebase-adminsdk-fbsvc-aa7980f96c.json")
firebase_admin.initialize_app(cred)

async def get_current_user(authorization: Optional[str] = Header(None)):
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
