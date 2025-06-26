def profile_serializer(profile) -> dict:
    return {
        "id": str(profile["_id"]),
        "user_id": profile["user_id"],
        "full_name": profile["full_name"],
        "phone_number": profile.get("phone_number"),
        "address": profile.get("address"),
        "date_of_birth": profile.get("date_of_birth"),
        "medical_history": profile.get("medical_history"),
        "allergies": profile.get("allergies"),
        "emergency_contact": profile.get("emergency_contact"),
        "blood_type": profile.get("blood_type")
    }

def profile_list_serializer(profiles) -> list:
    return [profile_serializer(profile) for profile in profiles]