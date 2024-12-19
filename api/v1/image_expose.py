from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/images/{filename}")
def serve_image(filename: str):
    return FileResponse(os.path.join(os.getcwd(), "images", filename))