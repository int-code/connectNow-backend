from fastapi import APIRouter, Depends, HTTPException, Header, status
from jose import JWTError
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from models import User, UsernameOnHold, Verification
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from schemas.authSchema import ForgotPassword, Token, CreateNewUser, CheckUsername, VerifyEmail, ResetPassword
from helper.authHelper import verify_password, hash_password, authenticate_user, generate_token, send_email, generate_6_digit_number
import jwt



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
  checkOnHold = db.query(UsernameOnHold).filter(UsernameOnHold.username == info.username).first()
  if (checkExisting is None) and (checkOnHold is None):
    return {"message": "Username is free to take"}
  raise HTTPException(status_code=400, detail="UsernameTaken")

@authRouter.post("/signup")
async def create_new_account(info: CreateNewUser,db: Session =Depends(get_db)):
  checkExisting = db.query(User).filter(User.email == info.email).first()
  if(not checkExisting is None):
     raise HTTPException(status_code=400, detail="UserAlreadyExists")
  checkExisting = db.query(User).filter(User.username == info.username).first()
  checkOnHold = db.query(UsernameOnHold).filter(UsernameOnHold.username == info.username).first()
  if not ((checkExisting is None) and (checkOnHold is None)):
     raise HTTPException(status_code=400, detail="UserNameTaken")
  checkExistingCode = db.query(Verification).filter(Verification.email == info.email).first()
  if not checkExistingCode is None:
     db.delete(checkExistingCode)
  email_code = generate_6_digit_number()
  await send_email({
      "to": [info.email],
      "subject": "Verification code",
      "body": f'Your verification code is {email_code}'
   })
  newVerification = Verification(email=info.email, code=email_code, used=False)
  db.add(newVerification)
  newUsernameOnHold = UsernameOnHold(username=info.username)
  db.add(newUsernameOnHold)
  db.commit()
  return {
     "message": "Verification code sent"
  }

@authRouter.post("/verify")
def verify_code(info: VerifyEmail, db:Session = Depends(get_db)):
   email = db.query(Verification).filter(Verification.email == info.email).first()
   if(email is None):
      raise HTTPException(status_code=400, detail="Verification code not generated")
   if(email.used):
      raise HTTPException(status_code=400, detail="Verification code already used")
   current_time = datetime.utcnow()
   time_difference = current_time - email.created_at
   fifteen_minutes = timedelta(minutes=15)
   if time_difference>fifteen_minutes:
      raise HTTPException(status_code=400, detail="Verification code expired")
   if info.code != email.code:
      raise HTTPException(status_code=400, detail="Wrong verification code")
   checkExisting = db.query(User).filter(User.email == info.email).first()
   if(not checkExisting is None):
      raise HTTPException(status_code=400, detail="UserAlreadyExists")
   newUser = User(email=info.email, password = hash_password(info.password), username=info.username, profile_pic="http://127.0.0.1:8000/profile_pic/default_user.jpg", profile_pic_path="default_user.jpg")
   username = db.query(UsernameOnHold).filter(UsernameOnHold.username == info.username).first()
   db.add(newUser)
   email.used = True
   db.delete(username)
   db.commit()
   return {"message": "NewUserCreated"}
   

@authRouter.post("/token", response_model=Token)
async def login(formData: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
  authentication  = authenticate_user(formData.username, formData.password, db)
  if authentication['flag']:
     token = generate_token(authentication['detail'].username, authentication['detail'].id, timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
     return {"access_token": token['access_token'],"refresh_token":token['refresh_token'],"expires":token['expires'], "token_type": "bearer"}
  raise HTTPException(status_code=400, detail=authentication['detail'])
     
  
@authRouter.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
   try:
      payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
      username: str = payload.get("username")
      id: str = payload.get("id")
      if username is None or id is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
      user = db.query(User).filter(User.username == username, User.id == id).first()
      if user is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
   except JWTError:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Generate a new access token
   access_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
   access_token = generate_token(username, user.id, access_expires)
   return {"access_token": access_token['access_token'],"refresh_token":access_token['refresh_token'],"expires":access_token['expires'], "token_type": "bearer"}


# @authRouter.get("/home")
# def home(token: str= Depends(get_token_from_header), db:Session= Depends(get_db)):
#   user = verify_token(token, db)
#   return {
#     "user": user
#   }

@authRouter.post('/forgot-password')
async def forgot_password(info: ForgotPassword,db: Session = Depends(get_db)):
   user = db.query(User).filter(User.email==info.email).first()
   if not user:
      raise HTTPException("User does not exist")
   checkExistingCode = db.query(Verification).filter(Verification.email == info.email).first()
   if not checkExistingCode is None:
      db.delete(checkExistingCode)
   email_code = generate_6_digit_number()
   await send_email({
         "to": [info.email],
         "subject": "Verification code",
         "body": f'Your verification code is {email_code}'
      })
   newVerification = Verification(email=info.email, code=email_code, used=False)
   db.add(newVerification)
   db.commit()
   return {
      "message": "Verification code sent"
   }

@authRouter.post("/reset-password")
def reset_password(info: ResetPassword, db: Session = Depends(get_db)):
   verification = db.query(Verification).filter(Verification.email == info.user_email).first()
   if(verification is None):
      raise HTTPException(status_code=400, detail="Verification code not generated")
   if(verification.used):
      raise HTTPException(status_code=400, detail="Verification code already used")
   current_time = datetime.utcnow()
   time_difference = current_time - verification.created_at
   fifteen_minutes = timedelta(minutes=15)
   if time_difference>fifteen_minutes:
      raise HTTPException(status_code=400, detail="Verification code expired")
   if info.code != verification.code:
      raise HTTPException(status_code=400, detail="Wrong verification code")
   user = db.query(User).filter(User.email==info.user_email).first()
   user.password = hash_password(info.new_password)
   db.commit()