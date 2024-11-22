
from api.v1 import flow
from api.v1.webhook import router as webhook_router
from fastapi import FastAPI


app = FastAPI()


app.include_router(webhook_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8082)
