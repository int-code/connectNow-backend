from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

picRouter = APIRouter(prefix="/profile_pic")


@picRouter.get('/{path}')
def get_image(path: str):
  file_path = f"profile_pics/{path}"
  if os.path.exists(file_path):
    return FileResponse(file_path)