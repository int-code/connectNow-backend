from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InterestClass(BaseModel):
    id: int
    project_id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True

class UserClass(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    bio: Optional[str] = None
    profile_pic: Optional[str] = None
    profile_pic_path: Optional[str] = None
    username: str
    created_at: datetime
    
class AddInterest(BaseModel):
    project_id: int

class UpdateInterest(BaseModel):
    project_id: int
    user_id: int
    status: str

class DeleteInterest(BaseModel):
    interest_id: int