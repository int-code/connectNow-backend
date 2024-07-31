from pydantic import BaseModel
from typing import Optional


class SearchProjects(BaseModel):
  search: str

class GetProjectsByUser(BaseModel):
  user_id: int