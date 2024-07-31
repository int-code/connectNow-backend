from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from helper.authHelper import get_token_from_header, verify_token
from helper.projectHelper import authenticateOwnerOrAdmin
from models import Skill, ProjectSkill, UserSkill
from schemas.skillSchema import AddSkill

skillRouter = APIRouter(prefix="/skill")

@skillRouter.get("/")
def get_skills(access_token:str = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  skills = db.query(Skill)
  return skills

@skillRouter.get('/project/{project_id}')
def get_skills_by_project(project_id, access_token:str = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  skills = db.query(Skill).join(ProjectSkill, ProjectSkill.skill_id==Skill.id).filter(ProjectSkill.project_id == project_id).all()
  return skills


@skillRouter.get('/user/{user_id}')
def get_skills_by_user(user_id, access_token:str = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  skills = db.query(Skill).join(UserSkill, UserSkill.skill_id==Skill.id).filter(UserSkill.user_id == user_id).all()
  return skills

@skillRouter.post('/')
def add_skills(info:AddSkill,
               access_token:str = Depends(get_token_from_header), 
               db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  if(not info.project_id is None):
    exists = db.query(ProjectSkill).filter(ProjectSkill.project_id==info.project_id, ProjectSkill.skill_id==info.skill_id).first()
    if exists:
      raise HTTPException(status_code=400, detail="SkillExists")
    authenticateOwnerOrAdmin(user, info.project_id, db)
    newSkill = ProjectSkill(project_id=info.project_id, skill_id=info.skill_id)
    db.add(newSkill)
    db.commit()
  else:
    exists = db.query(UserSkill).filter(UserSkill.user_id==user.id, UserSkill.skill_id==info.skill_id).first()
    if exists:
      raise HTTPException(status_code=400, detail="SkillExists")
    newSkill = UserSkill(user_id=user.id, skill_id=info.skill_id)
    db.add(newSkill)
    db.commit()



@skillRouter.delete('/')
def delete_skills(info:AddSkill,
               access_token:str = Depends(get_token_from_header), 
               db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  if(not info.project_id is None):
    exists = db.query(ProjectSkill).filter(ProjectSkill.project_id==info.project_id, ProjectSkill.skill_id==info.skill_id).first()
    if not exists:
      raise HTTPException(status_code=400, detail="SkillIsNotLinked")
    authenticateOwnerOrAdmin(user, info.project_id, db)
    db.delete(exists)
    db.commit()
  else:
    exists = db.query(UserSkill).filter(UserSkill.user_id==user.id, UserSkill.skill_id==info.skill_id).first()
    if not exists:
      raise HTTPException(status_code=400, detail="SkillIsNotLinked")
    db.delete(exists)
    db.commit()
