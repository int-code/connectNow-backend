from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from database import get_db
from sqlalchemy.orm import Session


interestRouter = APIRouter(prefix="/interest")


@interestRouter.get("/{project_id}")

@interestRouter.post('/')

@interestRouter.put('/')

@interestRouter.delete('/')