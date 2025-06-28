import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "MedicineAppDB")
MONGODB_APP_NAME = os.getenv("MONGODB_APP_NAME", "TryOut")

if not all([MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_CLUSTER]):
    raise ValueError("Missing required MongoDB environment variables. Please check your .env file.")

password = quote_plus(MONGODB_PASSWORD)

client = MongoClient(
    f"mongodb+srv://{MONGODB_USERNAME}:{password}@{MONGODB_CLUSTER}/?retryWrites=true&w=majority&appName={MONGODB_APP_NAME}"
)

# Unified database
db = client[MONGODB_DATABASE]

# Collections
profile_collection = db["profiles"]
medicine_collection = db["medicines"]
prescription_collection = db["prescriptions"]
messages_collection = db["messages"]  # Add this line
