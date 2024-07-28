from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import User
from helper.authHelper import get_token_from_header, verify_token
from typing import Annotated
import uuid
import os

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
  if not user.profile_pic is None:
    try:
      if not os.path.isfile(f"profile_pics/{user.profile_pic}"):
          raise HTTPException(status_code=404, detail="File not found")
      os.remove(f"profile_pics/{user.profile_pic}")
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  extension = profile_pic.filename.split(".")[-1]
  profile_pic.filename = str(uuid.uuid4())+"."+extension
  contents = await profile_pic.read()
  with open(f"profile_pics/{profile_pic.filename}", "wb") as f:
    f.write(contents)
  user.name = name
  user.bio = bio
  user.profile_pic = profile_pic.filename
  db.commit()
  return {"detail": "UserUpdated"}

@userRouter.delete('/')
def delete_user(access_token = Depends(get_token_from_header),
                db:Session=Depends(get_db)):
  user = verify_token(access_token, db)
  if not user.profile_pic is None:
    try:
      if not os.path.isfile(f"profile_pics/{user.profile_pic}"):
          raise HTTPException(status_code=404, detail="File not found")
      os.remove(f"profile_pics/{user.profile_pic}")
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  db.delete(user)
  db.commit()
  return {"detail": "UserDeleted"}
  