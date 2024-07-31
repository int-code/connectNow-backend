from pydantic import BaseModel
from typing import Optional


class AddSkill(BaseModel):
  project_id: Optional[int]=None
  skill_id: int
