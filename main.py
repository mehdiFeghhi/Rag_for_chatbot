from fastapi import FastAPI, status, Form, HTTPException, Depends, BackgroundTasks
# from .data.models import UserBase,UserOut,UserIn,Token,DirectoryListing
from data.models import UserBase,UserOut,UserIn,Token,Account
# from .data.user import is_user_exists, create_user
from data.user import is_user_exists, create_user
# from .utils.user_auth import authenticate_user,return_titimedelta,create_access_token,get_current_active_user
from utils.user_auth import authenticate_user,return_titimedelta,create_access_token,get_current_active_user,get_current_active_user_admin
from typing import Any,List,Annotated,Dict
from fastapi.responses import HTMLResponse
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import asyncio
import os
from fastapi import BackgroundTasks

 
PATH_DOCUMENT = "C:\\Users\\admin\\Desktop\\Franam"

# start_rag()

app = FastAPI()
api = "localhost"
port = "8000"
api_number = '127.0.0.1'
origins = [
    f"http://{api}",
    f"http://{api}:{port}",
    f"http://{api_number}",
    f"http://{api_number}:{port}",
    f"http://{api_number}:{port}/token",
    f"http://{api_number}:{port}/register",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST","PUT"],
    allow_headers=["*"],
)


@app.post("/token", status_code=status.HTTP_200_OK) 
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = return_titimedelta()
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")





@app.post("/main/register", status_code=status.HTTP_201_CREATED )
async def register(
    person: UserIn, 
    current_user: Annotated[UserBase, Depends(get_current_active_user_admin)]
) -> dict[str, UserOut]:
    # Check if the current user is an administrator
    # if current_user.role.type != "Administrator":
    #     raise HTTPException(status_code=405, detail="METHOD NOT ALLOWED")

    # Check if the user already exists
    if  is_user_exists(person.username):
        raise HTTPException(status_code=400, detail="USER ALREADY EXISTS")

    person_save = create_user(person)
    return {"Person": person_save}




