####LIBRARY IMPORTS####
#import json
import logging
import bcrypt

####LOCAL IMPORTS####
from database.db import mongo_obj
from utils.db_utils import user_exists, email_exists
from exceptions.registrationExceptions import UserAlreadyExists, EmailAlreadyExists
from exceptions.authenticationExceptions import UserNotFoundError, InvalidPasswordError

##INITIALIZE LOGGING##
logger = logging.getLogger(__name__)

##SET UP DATABASE CONNECTION##
mongo_db = mongo_obj.mongo_db

def register_user(username, email, password):
    """
    Creates a new user in the database.

    Note:
        Exceptions occuring/raised in this function are intended to be handled by the caller.

    Exceptions:
        UserAlreadyExists: If a username is already taken. (exceptions.registrationException)
        PyMongoError: For general database operation error. (pymongo.errors)   
    """

    if user_exists(username):
        raise UserAlreadyExists(f"Username {username} has already been taken")
    if email_exists(email):
        raise EmailAlreadyExists("Email already exists")



    auth_collection = mongo_db['auth']
    user_collection = mongo_db['user']

    auth_data = {
        "username": username,
        "password": password
    }

    auth_user_id = auth_collection.insert_one(auth_data).inserted_id

    user_profile = {    
        "_id": auth_user_id,
        "username": username,
        "email": email
    }

    user_collection.insert_one(user_profile)

    logger.info(f"User {username} registered successfully with id {auth_user_id}")



def authenticate_user(username, password):
    """
    Authenticates a user.

    Note:
        Exceptions occuring/raised in this function are intended to be handled by the caller.

    Exceptions:
        UserNotFoundError: If a username is not found in the database. (exceptions.authenticationExceptions)
        InvalidPasswordError: If the password is incorrect. (exceptions.authenticationExceptions)
        PyMongoError: For general database operation error. (pymongo.errors)   
    """
    if user_exists(username):
        collection = mongo_db['auth']

        db_password = collection.find_one({"username": username})['password']

        if not bcrypt.checkpw(password.encode('utf-8'), db_password):
            raise InvalidPasswordError("Invalid password")
    
    else:
        raise UserNotFoundError(f"User {username} does not exist")
    

