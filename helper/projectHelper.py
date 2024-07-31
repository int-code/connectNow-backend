from models import Project, Members
from fastapi import HTTPException


def authenticateOwnerOrAdmin(user,project_id, db):
  project = db.query(Project).filter(Project.id == project_id).first()
  if not project:
    raise HTTPException(status_code=404, detail="ProjectNotFound")
  
  if user.id == project.admin_id:
    pass
  else:
    member = db.query(Members).filter(
        Members.project_id == project_id,
        Members.user_id == user.id,
        Members.role == "admin"
    ).first()
    
    if not member:
      raise HTTPException(status_code=403, detail="ActionNotPermitted")