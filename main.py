from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import profile_route
from routes.medicines import medicine_route
from routes.prescription import add_prescription

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_route.router)
app.include_router(medicine_route.router)
app.include_router(add_prescription.router)