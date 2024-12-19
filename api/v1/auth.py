from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.agents import UserCreate, UserLogin
from utils import auth
from database.elasticsearch import Elastic
from passlib.context import CryptContext
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

import os


load_dotenv()

cert_path = os.path.join(os.getcwd(), "database", "http_ca.crt")
elastic = Elastic("https://127.0.0.1:9200", "elastic", os.getenv("ELASTIC_PASSWORD"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=12)

auth_router = APIRouter()
oaut2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oaut2_scheme)):
    return auth.verify_access_token(token)


@auth_router.post("/create_user")
def create_user(user: UserCreate, current_user: UserLogin = Depends(get_current_user)):
    if elastic.find("agents", user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(user.password)
    elastic.add("agents", {"username": user.username, "password": hashed_password, "roles": user.roles}, id=user.username)
    return {"message": "User created successfully"}




@auth_router.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = elastic.find("agents", form_data.username)
    if not user_data or not pwd_context.verify(form_data.password, user_data["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = auth.create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

