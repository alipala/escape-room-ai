from pydantic import BaseModel

class GameCreate(BaseModel):
    user_id: int
    theme: str
    difficulty: int
    age_group: str