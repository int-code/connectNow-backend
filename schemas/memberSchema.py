from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MembersClass(BaseModel):
  id: int
  project_id: int
  user_id: int
  role: str
  joined_at: Optional[datetime] = None
  

class AddMembers(BaseModel):
  project_id: int
  user_id: int
  role: str