
from api.v1 import flow
from api.v1.webhook import router as webhook_router
from api.v1.db_expose import router as db_router
from api.v1.image_expose import router as image_router
from api.v1.auth import auth_router as auth_router
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware



load_dotenv(".env")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)


app.include_router(webhook_router)
app.include_router(db_router)
app.include_router(image_router)
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8082)
