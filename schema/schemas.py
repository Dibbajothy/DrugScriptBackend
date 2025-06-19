def individual_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),  # MongoDB uses "_id" for the document ID
        "name": todo["name"],
        "description": todo["description"],
        "completed": todo["completed"],
        "user_id": todo["user_id"]
    }

def list_serializer(todos) -> list:
    return [individual_serializer(todo) for todo in todos]