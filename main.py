from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
from fastapi.middleware.cors import CORSMiddleware
import routes
import routes.medicines
import routes.medicines.medicine_route
import routes.route;

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your Flutter app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.route.router)
app.include_router(routes.medicines.medicine_route.router)