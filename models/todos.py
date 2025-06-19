from pydantic import BaseModel
from typing import Optional

class Todo(BaseModel):
    name : str
    description: str
    completed: bool
    user_id: Optional[str] = None  # Make user_id optional
