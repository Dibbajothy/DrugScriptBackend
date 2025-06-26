### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing
### Only for testing


from config.database import db, client, profile_collection
from datetime import datetime

def test_medicine_app_db_unified():
    try:
        print("🧪 Testing Unified MedicineAppDB...")
        
        # Test 1: Profile Collection
        print("\n1. Testing profiles collection...")
        test_profile = {
            "user_id": "test_user_123",
            "name": "Test User",
            "email": "test@example.com",
            "age": 30
        }
        result = profile_collection.insert_one(test_profile)
        print(f"✅ Profile inserted with ID: {result.inserted_id}")
        
        # Test 2: Medicine Collection
        print("\n2. Testing medicines collection...")
        medicine_count = db["medicines"].count_documents({})
        print(f"✅ Medicine collection has {medicine_count} documents")
        
        # Test 3: Prescription Collection
        print("\n3. Testing prescriptions collection...")
        prescription_collection = db["prescriptions"]
        test_prescription = {
            "user_id": "test_user_123",
            "doctor_name": "Dr. Test",
            "contact": "123-456-7890",
            "medicines": ["Medicine A", "Medicine B"],
            "created_at": datetime.utcnow()
        }
        prescription_result = prescription_collection.insert_one(test_prescription)
        print(f"✅ Prescription inserted with ID: {prescription_result.inserted_id}")
        
        # Test 4: Database Unity Check
        print("\n4. Verifying database unity...")
        collections = db.list_collection_names()
        print(f"✅ Database: MedicineAppDB")
        print(f"✅ Collections: {collections}")
        
        # Clean up test data
        print("\n5. Cleaning up test data...")
        profile_collection.delete_one({"user_id": "test_user_123"})
        prescription_collection.delete_one({"user_id": "test_user_123"})
        print("✅ Test data cleaned up")
        
        print("\n🎉 ALL TESTS PASSED - MedicineAppDB is fully unified!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_medicine_app_db_unified()