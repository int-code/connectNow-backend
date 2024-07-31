from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SearchProjects(BaseModel):
  search: str

class GetProjectsByUser(BaseModel):
  user_id: int


class ProjectClass(BaseModel):
  id: int
  admin_id: int
  name: str
  description: Optional[str] = None
  pic_url: Optional[str] = None
  pic_path: Optional[str] = None
  status: str
  created_at: datetime