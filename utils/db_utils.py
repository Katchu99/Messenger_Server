####LIBRARY IMPORTS####
import logging
from bson.objectid import ObjectId

####LOCAL IMPORTS####
from database.db import mongo_obj

####EXCEPTION IMPORTS####
from exceptions.authenticationExceptions import UserNotFoundError

##INITIALIZE LOGGING##
logger = logging.getLogger(__name__)

####INITIALIZE DATABASE####
mongo_db = mongo_obj.mongo_db

def user_exists(username) -> bool:
    collection = mongo_db['auth']
    user = collection.find_one({"username": username})
    return user is not None

def email_exists(email) -> bool:
    collection = mongo_db['user']
    email = collection.find_one({"email": email})
    return email is not None

def get_id_by_name(username) -> ObjectId:
    collection = mongo_db['auth']
    user = collection.find_one({"username": username})
    if user:
        return user['_id']
    else:
        raise UserNotFoundError(f"User with username {username} does not exist.")

def get_name_by_id(user_id) -> str:
    collection = mongo_db['auth']
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user['username']
    else:
        raise UserNotFoundError(f"User with ID {user_id} does not exist.")