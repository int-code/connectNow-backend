from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse
from database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import User
from helper.authHelper import get_token_from_header, verify_token
from typing import Annotated
import uuid
import os
from config import BASE_URL

userRouter = APIRouter(prefix="/user")

@userRouter.get('/')
def get_user(access_token = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  return {
    "username": user.username,
    "email": user.email,
    "name": user.name,
    "bio": user.bio,
    "profile_pic": user.profile_pic
  }

@userRouter.post('/')
async def update_user(name: Annotated[str, Form()],
                bio: Annotated[str, Form()],
                profile_pic: Annotated[UploadFile, File()],
                access_token = Depends(get_token_from_header),
                db:Session=Depends(get_db)):
  user = verify_token(access_token, db)
  if not user.profile_pic_path is None:
    try:
      if not os.path.isfile(f"profile_pics/{user.profile_pic}"):
          raise HTTPException(status_code=404, detail="File not found")
      os.remove(f"profile_pics/{user.profile_pic_path}")
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  user.profile_pic ="http://127.0.0.1:8000/profile_pic/default_user.jpg"
  user.profile_pic_path = "default_user.jpg"
  if not profile_pic is None:
    extension = profile_pic.filename.split(".")[-1]
    profile_pic.filename = str(uuid.uuid4())+"."+extension
    contents = await profile_pic.read()
    with open(f"profile_pics/{profile_pic.filename}", "wb") as f:
      f.write(contents)
    user.profile_pic = BASE_URL+"/profile_pic/"+profile_pic.filename
    user.profile_pic_path = profile_pic.filename
  user.name = name
  user.bio = bio
  db.commit()
  return {"message": "UserUpdated"}

@userRouter.delete('/')
def delete_user(access_token = Depends(get_token_from_header),
                db:Session=Depends(get_db)):
  user = verify_token(access_token, db)
  if not user.profile_pic is None:
    try:
      if not os.path.isfile(f"profile_pics/{user.profile_pic_path}"):
          raise HTTPException(status_code=404, detail="File not found")
      if not user.profile_pic_path == "default_user.jpg":
        os.remove(f"profile_pics/{user.profile_pic_path}")
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  db.delete(user)
  db.commit()
  return {"message": "UserDeleted"}


@userRouter.get('/{user_id}')
def get_user_by_id(user_id, access_token = Depends(get_token_from_header), db:Session = Depends(get_db)):
  user = verify_token(access_token, db)
  viewUser = db.query(User).filter(User.id==user_id).first()
  isUser = False
  if(user.id == user_id):
    isUser = True
  return {
    "username": viewUser.username,
    "email": viewUser.email,
    "name": viewUser.name,
    "bio": viewUser.bio,
    "profile_pic": viewUser.profile_pic,
    "isUser": isUser,
    "joined_at": viewUser.created_at
  }