from fastapi import Depends, HTTPException, status, FastAPI
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db
from routes.auth import authRouter
from routes.user import userRouter
from routes.profile_pic import picRouter
from routes.project import projectRouter
from routes.members import membersRouter
from routes.interest import interestRouter
from routes.skill import skillRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "*"],  # You can replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"]
)


@app.get("/")
async def index_function(db: Session = Depends(get_db)):
  return {"Server is running!"}

app.include_router(authRouter)
app.include_router(userRouter)
app.include_router(picRouter)
app.include_router(projectRouter)
app.include_router(membersRouter)
app.include_router(interestRouter)
app.include_router(skillRouter)