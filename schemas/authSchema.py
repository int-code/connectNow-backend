from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str

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