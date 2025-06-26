def profile_serializer(profile) -> dict:
    return {
        "id": str(profile["_id"]),
        "user_id": profile["user_id"],
        "email": profile.get("email"),
        "name": profile.get("name", ""),
        "age": profile.get("age"),
        "address": profile.get("address"),
        "gender": profile.get("gender"),
        "phone": profile.get("phone"),
        "date_of_birth": profile.get("date_of_birth"),
        "blood_type": profile.get("blood_type"),
        "allergies": profile.get("allergies"),
        "medical_conditions": profile.get("medical_conditions"),
        "emergency_contact": profile.get("emergency_contact")
    }

def profile_list_serializer(profiles) -> list:
    return [profile_serializer(profile) for profile in profiles]