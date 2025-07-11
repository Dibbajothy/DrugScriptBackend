import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import profile_route
from routes.medicines import medicine_route
from routes.prescription import add_prescription
from routes.chat_channel import router as chat_channel
from routes.qrCodes import scanqr
from routes.sharing import recieved
from routes.sharing import sent
from routes.Reviews import clinic_review
# from config.database import test_database_connection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DrugScript API",
    description="A medical prescription and medicine management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test database connection on startup
# @app.on_event("startup")
# async def startup_event():
#     """Test database connection when the app starts"""
#     if not test_database_connection():
#         raise Exception("Failed to connect to database")

# Include routers
app.include_router(profile_route.router)
app.include_router(medicine_route.router)
app.include_router(add_prescription.router)
app.include_router(chat_channel)
app.include_router(clinic_review.router)
app.include_router(scanqr.router)
app.include_router(recieved.router)
app.include_router(sent.router)

@app.get("/")
async def root():
    return {
        "message": "DrugScript API is running",
        "database": os.getenv("MONGODB_DATABASE"),
        "status": "healthy",
        "auto_registration": "enabled"
    }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     db_status = test_database_connection()
#     return {
#         "status": "healthy" if db_status else "unhealthy",
#         "database_connected": db_status,
#         "database_name": os.getenv("MONGODB_DATABASE")
#     }