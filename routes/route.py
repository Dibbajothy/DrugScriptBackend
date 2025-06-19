from fastapi import APIRouter, Depends
from models.todos import Todo
from config.database import collection_name
from schema.schemas import list_serializer
from bson import ObjectId
from auth.firebase_auth import get_current_user

router = APIRouter()

# Get Request Method / Fetch all todos for a user
@router.get("/")
async def get_todos(user_id: str = Depends(get_current_user)):
    todos = list_serializer(collection_name.find({"user_id": user_id}))
    return todos 





# # Post Request Method / Create a new todo
# @router.post("/")
# async def create_todo(todo: Todo, user_id: str = Depends(get_current_user)):
#     # Ensure the user_id in the todo matches the authenticated user
#     todo_dict = dict(todo)
#     todo_dict["user_id"] = user_id
#     collection_name.insert_one(todo_dict)
#     return {"message": "Todo created successfully"}



# Post Request Method / Create a new todo
@router.post("/")
async def create_todo(todo: Todo, user_id: str = Depends(get_current_user)):
    # Create a dictionary from the todo and update the user_id
    todo_dict = dict(todo)
    todo_dict["user_id"] = user_id  # Override any user_id that was provided or add if missing
    
    # Insert into database
    collection_name.insert_one(todo_dict)
    return {"message": "Todo created successfully"}




# PUT Request Method / Update a todo
@router.put("/{id}")
async def update_todo(id: str, todo: Todo, user_id: str = Depends(get_current_user)):
    # First check if the todo belongs to the user
    existing_todo = collection_name.find_one({"_id": ObjectId(id)})
    if not existing_todo or existing_todo.get("user_id") != user_id:
        return {"error": "Todo not found or not authorized"}
    
    todo_dict = dict(todo)
    todo_dict["user_id"] = user_id  # Ensure user_id remains correct
    collection_name.update_one(
        {"_id": ObjectId(id)},
        {"$set": todo_dict}
    )
    return {"message": "Todo updated successfully"}

# Delete Request Method / Delete a todo
@router.delete("/{id}")
async def delete_todo(id: str, user_id: str = Depends(get_current_user)):
    # First check if the todo belongs to the user
    existing_todo = collection_name.find_one({"_id": ObjectId(id)})
    if not existing_todo or existing_todo.get("user_id") != user_id:
        return {"error": "Todo not found or not authorized"}
    
    collection_name.delete_one({"_id": ObjectId(id)})
    return {"message": "Todo deleted successfully"}