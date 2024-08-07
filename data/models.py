from pydantic import BaseModel
from typing import List


class Role(BaseModel):
    description: str
    type: str


class Admin(Role):
    type: str = "Administrator"


class NormalUser(Role):
    type: str = "User"

class Owner(Role):
    type: str = "Owner"


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


class Folder(BaseModel):
    folder_name:str
    have_Rag:bool
    Rag_embedder:str | None = None

class Folder_User(BaseModel):
    folder_name:str
    username:str
    role: Role