from pydantic import BaseModel
from typing import List
from datetime import timedelta

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires: timedelta

class CreateNewUser(BaseModel):
    email: str
    username: str
    password: str

class CheckUsername(BaseModel):
   username: str

class AuthenticateUser(BaseModel):
   flag: bool
   detail: str

class MailBody(BaseModel):
    to: List[str]
    subject: str
    body: str

class VerifyEmail(BaseModel):
    email: str
    code: int
    password: str
    username: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    code: int
    new_password: str
    user_email: str