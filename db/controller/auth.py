import sys
sys.path.append('..')

import bcrypt
import uuid

from db.auth import data_obj, logger
from db.controller.auth_utils import check_if_exists
from exceptions.customExceptions import AuthError

def register_user(username, password): #TODO: exception throwing
    if not check_if_exists(username):
        sql = '''INSERT INTO users (id, username, password) VALUES (%s, %s, %s)'''
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        values = (uuid.uuid4().hex, username, hashed_password)
        data_obj.cursor.execute(sql, values)
        data_obj.connection.commit()
        logger.info(f"User {username} registered successfully.")
        return "Successful"
    else:
        logger.warning(f"Attempt to register taken username: {username}")
        return "Username already taken!"

def authenticate_user(username, password):
    if check_if_exists(username):
        sql = '''SELECT password FROM users WHERE username=%s'''
        values = (username, )
        data_obj.cursor.execute(sql, values)
        hashed_password = data_obj.cursor.fetchone()[0]

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            raise AuthError("Invalid password")
    
    else:
        raise AuthError("User does not exist")
