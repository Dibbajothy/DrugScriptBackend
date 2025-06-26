def profile_serializer(profile) -> dict:
    return {
        "id": str(profile["_id"]),
        "user_id": profile["user_id"],
        "email": profile.get("email"),
        "name": profile["name"],
        "age": profile["age"],
        "address": profile["address"],
        "gender": profile["gender"],
        "phone": profile["phone"],
        "date_of_birth": profile["date_of_birth"],
        "blood_type": profile["blood_type"],
        "allergies": profile.get("allergies"),
        "medical_conditions": profile.get("medical_conditions"),
        "emergency_contact": profile["emergency_contact"]
    }

def profile_list_serializer(profiles) -> list:
    return [profile_serializer(profile) for profile in profiles]