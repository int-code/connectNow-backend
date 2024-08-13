from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from database import get_db
from sqlalchemy.orm import Session
from helper.authHelper import get_token_from_header, verify_token
from helper.projectHelper import authenticateOwnerOrAdmin
from models import Members, Project, Interest, User
from schemas.interestSchema import DeleteInterest, InterestClass, UpdateInterest, UserClass, AddInterest

interestRouter = APIRouter(prefix="/interest")


@interestRouter.get("/{project_id}")
def get_interests(project_id,
                  access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token,db)
  project = db.query(Project).query(Project.id == project_id).first()
  if not project:
    raise HTTPException(status_code=400, detail="ProjectDoesNotExist")
  interests = db.query(Interest, User).join(User, Interest.user_id == User.id).filter(Interest.project_id == project_id).all()

  formatted_interests = [
    {
      "interest": InterestClass.model_validate(interest),
      "user": UserClass.model_validate(user)
    }
    for interest, user in interests
  ]

  return formatted_interests

@interestRouter.post('/')
def add_interest(info: AddInterest,
                access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  existing = db.query(Interest).filter(Interest.project_id==info.project_id, Interest.user_id==user.id).first()
  member = db.query(Members).filter(Members.project_id==info.project_id, Members.user_id==user.id).first()
  if member:
    raise HTTPException(status_code=400, detail="AlreadyMember")
  if existing:
    raise HTTPException(status_code=400, detail="InterestExists")
  NewInterest = Interest(project_id=info.project_id, user_id=user.id, status="waiting")
  db.add(NewInterest)
  db.commit()
  return {
    "detail": "InterestAdded"
  }

@interestRouter.put('/')
def update_interest(info: UpdateInterest,
                access_token:str = Depends(get_token_from_header), 
                 db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  authenticateOwnerOrAdmin(user, info.project_id, db)
  interest = db.query(Interest).filter(Interest.project_id==info.project_id, Interest.user_id==info.user_id).first()
  interest.status = info.status
  if(info.status == "accepted"):
    existing = db.query(Members).filter(Members.project_id == info.project_id, Members.user_id==info.user_id).first()
    if existing:
      raise HTTPException(status_code=400, detail="AlreadyAMember")
    newMember = Members(project_id=info.project_id, user_id=info.user_id, role="member")
    db.add(newMember)
  db.commit()
  return {"messsage", "InterestUpdated"}

@interestRouter.delete('/')
def delete_interest(info:DeleteInterest,
                    access_token:str = Depends(get_token_from_header), 
                    db: Session = Depends(get_db)):
  user = verify_token(access_token, db)
  interest = db.query(Interest).filter(Interest.id==info.interest_id).first()
  if not interest:
    raise HTTPException(status_code=400, detail="InterestNotExists")
  if interest.user_id != user.id:
    raise HTTPException(status_code=400, detail="ActionNotPermitted")
  if interest.status != "waiting":
    raise HTTPException(status_code=400, detail="InterestDecided")
  db.delete(interest)
  db.commit()
  return {"message": "InterestDeleted"}
