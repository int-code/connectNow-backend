import smtplib
import binascii
from ssl import create_default_context
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import bcrypt
from schemas.authSchema import AuthenticateUser, MailBody
from models import User
from datetime import datetime, timedelta, timezone
from config import MAIL_HOST,MAIL_PASSWORD, MAIL_PORT, MAIL_USERNAME
from config import SECRET_KEY, ALGORITHM
from fastapi import Header, status, HTTPException
import jwt


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hassed_byte_enc = binascii.unhexlify(hashed_password.replace('\\x', ''))
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hassed_byte_enc)


def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

def authenticate_user(username, password, db) -> AuthenticateUser:
   userExists = db.query(User).filter(User.username==username).first()
   if(userExists is None):
      return {"flag": False, "detail": "UserNotExists"}
   if verify_password(password, userExists.password):
      return {"flag": True, "detail": userExists}
   return {"flag": False, "detail": "PasswordIncorrect"}

def generate_token(username, id, expires):
   encode = {"username": username, "id": id}
   refresh_token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
   expireTime = datetime.utcnow()+expires
   encode.update({"exp": expireTime})
   access_token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
   return {"access_token": access_token, "refresh_token": refresh_token, "expires": expires}

async def send_email(data:dict):
   message = MailBody(**data)
   msg = MIMEText(message.body, "html")
   msg["FROM"] = MAIL_USERNAME
   msg["TO"] = ','.join(message.to)
   msg["SUBJECT"] = message.subject
   print(msg)
   try:
      with SMTP_SSL(MAIL_HOST, MAIL_PORT) as server:
          server.login(MAIL_USERNAME, MAIL_PASSWORD)
          server.sendmail(MAIL_USERNAME, message.to, msg.as_string())
      return True
   except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return False
   except Exception as e:
      print(e)
      return False

   # message = MessageSchema(
   #      subject="Fastapi-Mail module",
   #      recipients=["pubalibasak56@gmail.com"],
   #      body="<p>Hello this is a new email Im trying</p>",
   #      subtype=MessageType.html)

   # fm = FastMail(conf)
   # try:
   #    await fm.send_message(message)
   # except Exception as e:
   #    print(e)




def get_token_from_header(access_token: str = Header(None)):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return access_token


def verify_token(token: str, db):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception
    user = db.query(User).filter(User.username==username).first()
    if user is None:
        raise credentials_exception
    return user

