import json
from .models import UserInDB,UserIn,UserOut
# from ..utils.security import get_password_hash
from utils.security import get_password_hash

from .database import db

def get_user(username: str):
    # Retrieve the user document from the users collection
    user_dict = db['users'].find_one({"username": username})
    
    # If user not found, return None
    if user_dict is None:
        return None

    # Convert the user document to a UserInDB object
    return UserInDB(**user_dict)


def is_user_exists(username:str) -> bool:
    user_dict =  db['users'].find_one({"username": username})
    # If user not found, return False
    if user_dict is None:
        return False
    else:
        return True
    

def create_user(person: UserIn):

    # Hash the user's password
    hashed_password = get_password_hash(person.password)
    
    # Create a UserInDB object
    user_in_db = UserInDB(
        username=person.username,
        full_name=person.full_name,
        role=person.role,
        disabled=person.disabled,
        hashed_password=hashed_password
    )

    # Save the new user to the database
    db['users'].insert_one(json.loads(user_in_db.model_dump_json()))

    # Create a UserOut object for the response
    person_save = UserOut(
        username=person.username,
        full_name=person.full_name,
        role=person.role,
        disabled=person.disabled
    )
    return person_save
