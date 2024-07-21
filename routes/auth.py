from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from schema import Token
authRouter = APIRouter(prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

@authRouter.post("/token")
async def generate_token(formData: OAuth2PasswordRequestForm = Depends()):
  print(formData)
  return {"access_token": formData.username, "token_type": "bearer"}


@authRouter.get("/home")
def home(token: str = Depends(oauth2_scheme)):
  print(token)
  return {
    "user": token
  }