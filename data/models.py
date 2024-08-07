from pydantic import BaseModel
from typing import List


class Role(BaseModel):
    description: str
    type: str


class Admin(Role):
    type: str = "Administrator"


class NormalUser(Role):
    type: str = "User"


class UserBase(BaseModel):
    username: str
    full_name: str
    role: Role | None = NormalUser
    disabled: bool | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Chat(BaseModel):
    username: str 
    topic: str
    description: str
    chat_history: List
    total_token_count: int | None = 0
    total_token_use_as_input: int | None = 0
    total_token_use_as_output: int | None = 0
    can_use: int | None = True
class Account(BaseModel):
    username: str
    model_name:str
    api_key: str
    company_name: str
    total_token_output: int | None = 0
    total_token_input: int | None = 0

    
