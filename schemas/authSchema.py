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