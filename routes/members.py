from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from database import get_db
from sqlalchemy.orm import Session
from helper.authHelper import get_token_from_header, verify_token
from helper.projectHelper import authenticateOwnerOrAdmin
from models import Members, Project
from schemas.memberSchema import AddMembers, MembersClass

membersRouter = APIRouter(prefix="/members")

@membersRouter.get('/{project_id}')
def get_members(project_id,
                access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  members = db.query(Members, Project).filter(Project.id==Members.project_id).filter(Project.id==project_id).all()
  membersResult = [ MembersClass.model_validate(mem) for mem, _ in members]

@membersRouter.post('/')
def add_members(info:AddMembers,
                access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)

  project = db.query(Project).filter(Project.id == info.project_id).first()
  if not project:
      raise HTTPException(status_code=404, detail="ProjectNotFound")
  
  if user.id == project.admin_id:
      pass
  else:
      member = db.query(Members).filter(
          Members.project_id == info.project_id,
          Members.user_id == user.id,
          Members.role == "admin"
      ).first()
      
      if not member:
          raise HTTPException(status_code=403, detail="ActionNotPermitted")
  
  existing_member = db.query(Members).filter(
      Members.project_id == info.project_id,
      Members.user_id == info.user_id
  ).first()
  
  if existing_member:
      raise HTTPException(status_code=400, detail="MemberAlreadyExists")

  new_member = Members(project_id=info.project_id, user_id=info.user_id, role=info.role)
  db.add(new_member)
  db.commit()
  
  return {"detail": "MemberAdded"}

@membersRouter.put('/')
def update_members(info:AddMembers,
                access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  authenticateOwnerOrAdmin(user, info.project_id, db)
  UpdateUser = db.query(Members).filter(Members.project_id==info.user_id, Members.user_id==info.user_id).first()
  UpdateUser.role = info.role
  db.commit()
  return {
     "detail": "MemberUpdated"
  }

@membersRouter.delete('/')
def delete_members(info:AddMembers,
                access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  project = db.query(Project).filter(Project.id == info.project_id).first()
  if not project:
    raise HTTPException(status_code=404, detail="ProjectNotFound")
  if user.id == project.admin_id:
    member = db.query(Members).filter(Members.project_id==info.project_id, Members.user_id==info.user_id).first()
    if member:
      db.delete(project)
      db.commit()
      return {
        "detail": "MemberRemoved"
      }
    else:
       raise HTTPException(status_code=400, detail="MembershipNotFound")
  else:
     raise HTTPException(status_code=403, detail="ActionNotPermitted")
  