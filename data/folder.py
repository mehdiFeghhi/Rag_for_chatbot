from .database import db
from .models import Folder,Folder_User,Role
import os

def get_folders(username: str):
    pass


def get_folder_by_name(folder_name:str) -> Folder:
    
    db_folders = db['folders']
    existing_folder = db_folders.find_one({"folder_name": folder_name})

    return Folder(**existing_folder)


def add_folder(folder_name:str,have_Rag:bool, Rag_embedder:str) -> None:
    
    try:
        os.mkdir(f"Main_folder/{folder_name}")
    except FileExistsError:
        raise("Folder already exists")

    db_folders = db['folders']
    folder = Folder(folder_name=folder_name, have_Rag=False, Rag_embedder=None)
    folder_id = db_folders.insert_one(folder.model_dump).inserted_id

def add_folder_user(folder_name:str, username:str, role:Role) -> None:

    folder_user = Folder_User(folder_name, username, role)
    db_folder_users = db['folder_users']
    db_folder_users.insert_one(folder_user.model_dump)


def find_user_folder(folder_name:str,username:str):

    db_folder_users = db['folder_users']
    existing_folder_user = db_folder_users.find_one({"folder_name": folder_name,"username":username})
    return existing_folder_user is not None and Folder_User(**existing_folder_user) or None

