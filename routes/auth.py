from fastapi import APIRouter, Depends, HTTPException, Header, status
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from models import User
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.authSchema import Token, CreateNewUser, CheckUsername
from helper.authHelper import verify_password, hash_password, authenticate_user, generate_token, send_email

authRouter = APIRouter(prefix="/auth")

@authRouter.post("/emailtrial")
async def try_email():
   print(await send_email({
      "to": ["pubalibasak16@gmail.com"],
      "subject": "Verification pin",
      "body": "Your verification pin is 1234"
   }))

@authRouter.post("/checkUsername")
def check_username(info: CheckUsername, db:Session =Depends(get_db)):
  checkExisting = db.query(User).filter(User.username == info.username).first()
  if(checkExisting is None):
    return {"message": "Username is free to take"}
  raise HTTPException(status_code=400, detail="UsernameTaken")

@authRouter.post("/signup")
def create_new_account(info: CreateNewUser,db: Session =Depends(get_db)):
  checkExisting = db.query(User).filter(User.email == info.email).first()
  if(not checkExisting is None):
     raise HTTPException(status_code=400, detail="UserAlreadyExists")
  checkExisting = db.query(User).filter(User.username == info.username).first()
  if(not checkExisting is None):
     raise HTTPException(status_code=400, detail="UserNameTaken")
  newUser = User(email=info.email, password = hash_password(info.password), username=info.username)
  db.add(newUser)
  db.commit()
  return {"message": "NewUserCreated"}

@authRouter.post("/token", response_model=Token)
async def login(formData: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
  authentication  = authenticate_user(formData.username, formData.password, db)
  if authentication['flag']:
     token = generate_token(authentication['detail'].username, authentication['detail'].id, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
     return {"access_token": token, "token_type": "bearer"}
  raise HTTPException(status_code=400, detail=authentication['detail'])
     
  


# @authRouter.get("/home")
# def home(token: str= Depends(get_token_from_header), db:Session= Depends(get_db)):
#   user = verify_token(token, db)
#   return {
#     "user": user
#   }