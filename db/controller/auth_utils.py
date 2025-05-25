import sys
sys.path.append('..')

import bcrypt
import uuid
import json

from db.auth import data_obj, logger

def check_if_exists(username):
    sql = '''SELECT username FROM users WHERE username=%s'''
    values = (username,)
    data_obj.cursor.execute(sql, values)
    result = data_obj.cursor.fetchone()
    exists = result is not None
    logger.debug(f"Check if user exists ({username}): {exists}")
    return exists

def get_id_by_name(username):
    sql = '''SELECT id FROM users
            WHERE username=%s'''
    values = (username,)
    data_obj.cursor.execute(sql, values)
    row = data_obj.cursor.fetchone()
    
    if row:
        user_id = row[0]
        logger.debug(f"Get ID by username ({username}): {user_id}")
        return row[0]
    logger.debug(f"Get ID by username ({username}): None")
    return None

def get_name_by_id(user_id):
    sql = '''SELECT username FROM users
                WHERE id = %s'''
    values = (user_id,)
    data_obj.cursor.execute(sql, values)
    username = data_obj.cursor.fetchone()
    logger.debug(f"Get username by ID ({user_id}): {username}")
    return username
