from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from helper.authHelper import get_token_from_header, verify_token
from models import Project, Members, Interest, Skill, ProjectSkill, User
from schemas.projectSchema import SearchProjects, ProjectClass
from typing import Annotated
import uuid
from config import BASE_URL
import os

projectRouter = APIRouter(prefix="/project")

@projectRouter.get("/")
def get_all_projects(access_token:str = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  projects = db.query(Project).all()
  return projects


@projectRouter.post("/")
async def make_project(name: Annotated[str, Form()],
                 description: Annotated[str, Form()] = None,
                 pic: Annotated[UploadFile, File()] = None,
                 access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  pic_url = None
  pic_path = None
  if not pic is None:
    extension = pic.filename.split(".")[-1]
    pic.filename = str(uuid.uuid4())+"."+extension
    contents = await pic.read()
    with open(f"profile_pics/{pic.filename}", "wb") as f:
      f.write(contents)
    pic_url = BASE_URL+"/profile_pic/"+pic.filename
    pic_path = pic.filename
    
  project = Project(admin_id = user.id, name=name, description=description, pic_url=pic_url, pic_path=pic_path, status="Not started")
  db.add(project)
  db.commit()
  db.refresh(project)
  return {
    "project_id": project.id
  }



@projectRouter.delete("/{project_id}")
def delete_project(project_id, access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  owner = db.query(Project.admin_id).filter(Project.id == project_id).first()
  print(owner)
  if(user.id != owner[0]):
    raise HTTPException(status_code=400, detail="Not permitted to do that action")
  project = db.query(Project).filter(Project.id==project_id).first()
  db.delete(project)
  db.commit()

@projectRouter.post("/name")
def search_projects_by_name(info: SearchProjects,
                            access_token:str= Depends(get_token_from_header), 
                            db: Session = Depends(get_db)):

  user = verify_token(access_token, db)  
  projects = db.query(Project).filter(Project.name.like(f"%{info.search}%")).all()
  return projects

@projectRouter.post("/user")
def get_project_by_user(info:SearchProjects,
                        access_token:str= Depends(get_token_from_header), 
                        db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  projects = db.query(Project, User).filter(Project.admin_id==User.id).filter(or_(User.username.like(f"%{info.search}%"), User.name.like(f"%{info.search}%"))).all()
  participating = db.query(Project, Members, User).filter(Project.id==Members.project_id).filter(Members.user_id==User.id).filter(or_(User.username.like(f"%{info.search}%"), User.name.like(f"%{info.search}%"))).all()
  
  owned_projects = [{"project": ProjectClass.model_validate(proj)} for proj, _ in projects]
  member_projects = [{"project": ProjectClass.model_validate(proj)} for proj, _, _ in participating]
  
  return {
    "owner": owned_projects,
    "member": member_projects
  }

@projectRouter.post("/skill")
def get_project_by_skill(info:SearchProjects,
                        access_token:str= Depends(get_token_from_header), 
                        db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  participating = db.query(Project, Skill, ProjectSkill).filter(Project.id==ProjectSkill.project_id).filter(ProjectSkill.skill_id==Skill.id).fiter(Skill.name.like(f"%{info.search}%")).all()
  return {
    "projects": participating
  }

@projectRouter.get('/user/{user_id}')
def get_project_by_userid(user_id, 
                          access_token:str= Depends(get_token_from_header), 
                          db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  projects = db.query(Project).filter(Project.admin_id==user_id).all()
  participating = db.query(Project, Members).filter(Members.project_id == Project.id).filter(Members.user_id==user_id).all()
  return {
    "owned": projects,
    "member": participating
  }

@projectRouter.get("/skill/{skill_id}")
def get_project_by_skillid(skill_id,
                           access_token:str= Depends(get_token_from_header), 
                            db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  projects = db.query(Project, Skill, ProjectSkill).filter(Project.id==ProjectSkill.project_id).filter(ProjectSkill.skill_id==Skill.id).filter(Skill.id==skill_id).all()
  return {
    "projects": projects
  }

@projectRouter.get("/{project_id}")
def get_project(project_id: str,access_token:str = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  project = db.query(Project).filter(Project.id == project_id).first()
  members = db.query(Members).filter(Members.project_id == project_id).all()
  interests = db.query(Interest).filter(Interest.project_id == project_id).all()
  skills = db.query(Skill).join(ProjectSkill, ProjectSkill.skill_id==Skill.id).filter(ProjectSkill.skill_id==Skill.id, ProjectSkill.project_id==project_id).all()
  isMember = "False"
  CurrMember = db.query(Members).filter(Members.project_id==project_id, Members.user_id==user.id).first()
  if CurrMember:
    if CurrMember.role == "admin":
      isMember = 'admin'
    else:
      isMember = 'True'
  if project is None:
    raise HTTPException(status_code=400, detail="ProjectNotFound")
  return {
    "project": project,
    "members": members,
    "interests": interests,
    "isMember": isMember,
    "skills": skills
  }

@projectRouter.post("/{project_id}")
async def update_project(project_id,
                 name: Annotated[str, Form()],
                 description: Annotated[str, Form()] = None,
                 pic: Annotated[UploadFile, File()] = None,
                 access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  owner = db.query(Project.admin_id).filter(Project.id == project_id).first()
  print(owner)
  if(user.id != owner[0]):
    access = db.query(Members.role).filter(Members.project_id == project_id).filter(Members.user_id == user.id).first()
    if access is None:
      raise HTTPException(status_code=500, detail="Not permitted to do the action")
    if access != "ADMIN":
      raise HTTPException(status_code=500, detail="Not permitted to do the action")
  project = db.query(Project).filter(Project.id == project_id).first()
  if project is None:
    raise HTTPException(status_code=400, detail="ProjectNotFound")
  if not project.pic_path is None:
    try:
      if not os.path.isfile(f"profile_pics/{project.pic_path}"):
          raise HTTPException(status_code=404, detail="File not found")
      os.remove(f"profile_pics/{project.pic_path}")
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  project.pic_url = None
  project.pic_path = None
  if not pic is None:
    extension = pic.filename.split(".")[-1]
    pic.filename = str(uuid.uuid4())+"."+extension
    contents = await pic.read()
    with open(f"profile_pics/{pic.filename}", "wb") as f:
      f.write(contents)
    project.pic_url = BASE_URL+"/profile_pic/"+pic.filename
    project.pic_path = pic.filename
  project.name = name
  project.description = description
  db.commit()