from fastapi import FastAPI, status, Form, HTTPException, Depends, File, UploadFile
# from .data.models import UserBase,UserOut,UserIn,Token,DirectoryListing
from data.models import UserBase,UserOut,UserIn,Token,Owner
# from .data.user import is_user_exists, create_user
from data.user import is_user_exists, create_user
# from .utils.user_auth import authenticate_user,return_titimedelta,create_access_token,get_current_active_user
from utils.user_auth import authenticate_user,return_titimedelta,create_access_token,get_current_active_user,get_current_active_user_admin
from data.folder import get_folder_by_name,add_folder, add_folder_user, find_user_folder
from typing import Any,List,Annotated,Dict
from fastapi.responses import HTMLResponse
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import zipfile
import asyncio
import os

 
PATH_DOCUMENT = "C:\\Users\\admin\\Desktop\\Franam"

# start_rag()utils

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

    # Check if the user already exists
    if  is_user_exists(person.username):
        raise HTTPException(status_code=400, detail="USER ALREADY EXISTS")

    person_save = create_user(person)
    return {"Person": person_save}


@app.post("/main/folder", status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_name: str,  
    current_user: UserBase = Depends(get_current_active_user),
) -> Dict[str, str]:
    # Check if a folder with the same name already exists
    existing_folder = get_folder_by_name(folder_name)

    if existing_folder:
        # Raise an HTTPException with a 400 Bad Request status code
        raise HTTPException(status_code=400, detail="Folder with the same name already exists")

    # Create a new Folder instance
    # Insert the folder into the database
    add_folder(folder_name=folder_name, have_Rag=False, Rag_embedder=None)


    # Create a new Folder_User instance to link the folder to the current user
    # Insert the folder-user relationship into the database

    add_folder_user(folder_name=folder_name, username=current_user.username, role=Owner)


    # Return the created folder's details
    return {"folder_name": folder_name, "message": "Folder created successfully"}



@app.post("/main/upload_folder", status_code=status.HTTP_200_OK)
async def create_folder(
    folder_name: str,
    zip_file: UploadFile = File(...),  # Use File(...) to indicate that zip_file is a file upload
    current_user: UserBase = Depends(get_current_active_user),
) -> Dict[str, str]:


    folder_user = find_user_folder(folder_name,current_user.username)
    if folder_user is None or folder_user.role.type == 'User':
        raise HTMLResponse(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission to change in this folder.")

    # Create full destination path for extracted files
    destination_folder = os.path.join("/Main_folder", folder_name)
    # Ensure Main Folder exists
    if not os.path.isdir(destination_folder):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This folder not exist on server.")


    try:
        # Extract the zip file to the specified destination
        with zipfile.ZipFile(zip_file.file) as zip_ref:
            zip_ref.extractall(destination_folder)

        # Return a success message
        return {"message": f"Folder {folder_name} created successfully"}
    except Exception as e:
        # Raise an exception if something goes wrong
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

