from pymongo import MongoClient
from urllib.parse import quote_plus


password = quote_plus("hello@boy")
client = MongoClient(f"mongodb+srv://dibbajothy2:{password}@tryout.fwsnut6.mongodb.net/?retryWrites=true&w=majority&appName=TryOut")


# Use consistent database name
db = client.drugscript_db

# Collections
profile_collection = db["profile_collection"]
medicine_collection = db["new_medicines"]  # Added for consistency