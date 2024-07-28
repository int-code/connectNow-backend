from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from database import get_db
from sqlalchemy.orm import Session
from helper.authHelper import get_token_from_header, verify_token
from models import Project, Members
from schemas.projectSchema import getProject

projectRouter = APIRouter(prefix="/project")

@projectRouter.get("/")
def get_all_projects(access_token = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  projects = db.query(Project).all()
  return projects


@projectRouter.post("/{project_id}")
def get_project(project_id: str,access_token = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  project = db.query(Project, Members).filter(Members.project_id == Project.id).filter(Project.id == project_id).first()
  if project is None:
    raise HTTPException(status_code=400, detail="ProjectNotFound")
  return project

@projectRouter.get("/user/{user_id}")


@projectRouter.get("/filter")

@projectRouter.get("/filter/{project_id}")

@projectRouter.get("/filter/user/{user_id}")

@projectRouter.post("/")

@projectRouter.put("/")

@projectRouter.delete("/")

