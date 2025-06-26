from urllib.parse import quote_plus
from pymongo import MongoClient
from typing import Dict, List, Any
import math
from config.database import db, client  # Import from unified config

def clean_document(doc):
    """Replace NaN values with None to make JSON serializable"""
    if doc is None:
        return None
        
    if isinstance(doc, dict):
        for key, value in list(doc.items()):
            if isinstance(value, float) and math.isnan(value):
                doc[key] = None
            elif isinstance(value, dict) or isinstance(value, list):
                doc[key] = clean_document(value)
    elif isinstance(doc, list):
        for i, item in enumerate(doc):
            doc[i] = clean_document(item)
    
    return doc

def load_medicines() -> List[Dict[str, Any]]:
    """Load medicines from MongoDB and return as a list of dictionaries"""
    try:
        # Use unified database connection
        medicines_collection = db["medicines"]
        medicines = list(medicines_collection.find({}, {'_id': 0}))  # Exclude MongoDB _id from results
        
        # Clean NaN values in the data
        medicines = clean_document(medicines)
        
        print(f"Successfully loaded {len(medicines)} medicine entries from MedicineAppDB.")
        return medicines
    except Exception as e:
        print(f"Error retrieving data from MedicineAppDB: {e}")
        return []

def search_medicine(query: str) -> List[Dict[str, Any]]:
    """Search medicines by name, generic name using MongoDB, sorted by shortest name length"""
    try:
        # Use unified database connection
        medicines_collection = db["medicines"]
        
        results = list(medicines_collection.aggregate([
            # Match documents containing the query
            {
                "$match": {
                    "$or": [
                        {"medicine_name": {"$regex": query, "$options": "i"}},
                        {"generic_name": {"$regex": query, "$options": "i"}}
                    ]
                }
            },
            # Simply convert all fields to strings directly
            {
                "$addFields": {
                    "medicine_name_str": {"$toString": {"$ifNull": ["$medicine_name", ""]}},
                    "generic_name_str": {"$toString": {"$ifNull": ["$generic_name", ""]}}
                }
            },
            # Calculate lengths of the string versions
            {
                "$addFields": {
                    "medicine_name_length": {"$strLenCP": "$medicine_name_str"},
                    "generic_name_length": {"$strLenCP": "$generic_name_str"}
                }
            },
            # Add a field with the shorter of the two lengths
            {
                "$addFields": {
                    "shorter_length": {
                        "$cond": {
                            "if": {"$lte": ["$medicine_name_length", "$generic_name_length"]},
                            "then": "$medicine_name_length",
                            "else": "$generic_name_length"
                        }
                    }
                }
            },
            # Sort by the shorter length (ascending = shortest first)
            {
                "$sort": {"shorter_length": 1}
            },
            # Remove the temporary fields from results
            {
                "$project": {
                    "medicine_name_str": 0,
                    "generic_name_str": 0,
                    "medicine_name_length": 0,
                    "generic_name_length": 0,
                    "shorter_length": 0,
                    "_id": 0
                }
            }
        ]))
        
        # Clean NaN values in the results before returning
        results = clean_document(results)
        
        return results
    except Exception as e:
        print(f"Error searching medicines in MedicineAppDB: {e}")
        return []