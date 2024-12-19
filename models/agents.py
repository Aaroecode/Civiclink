from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    roles: list

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    roles: list
    
