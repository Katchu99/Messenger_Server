import sys
sys.path.append('..')

import bcrypt
import uuid
import json

from db.data import data_obj, logger
import db.controller.chats as chats

def create_user_table():
    data_obj.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id VARCHAR(255) PRIMARY KEY,
                            username VARCHAR(255),
                            password VARCHAR(255)
        )''')

    data_obj.connection.commit()
    logger.info("User table created or already exists.")

def create_chat_table():
    data_obj.cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name TEXT,
                            chat_member_ids JSON,
                            chat_content_id VARCHAR(255)
                            )''')
        
    data_obj.connection.commit()
    logger.info("Chat table created or already exists.")

def create_friends_table():
    data_obj.cursor.execute('''CREATE TABLE IF NOT EXISTS friends (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            userid1 INT,
                            userid2 INT,
                            status VARCHAR(50))''')
        
    data_obj.connection.commit()
    logger.info("Friends table created or already exists.")

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
    user_id = data_obj.cursor.fetchone()
    logger.debug(f"Get ID by username ({username}): {user_id}")
    return user_id

def get_name_by_id(user_id):
    sql = '''SELECT username FROM users
                WHERE id = %s'''
    values = (user_id,)
    data_obj.cursor.execute(sql, values)
    username = data_obj.cursor.fetchone()
    logger.debug(f"Get username by ID ({user_id}): {username}")
    return username

def register_user(username, password):
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
    sql = '''SELECT password FROM users WHERE username=%s'''
    values = (username, )
    data_obj.cursor.execute(sql, values)
    hashed_password = data_obj.cursor.fetchone()[0]
    if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        logger.info(f"User {username} authenticated successfully.")
        return True
    else:
        logger.warning(f"Failed authentication attempt for user: {username}")
        return False

# def send_friend_request(sender, receiver):
#     sender_id = data_obj.get_id_by_name(sender)
#     receiver_id = data_obj.get_id_by_name(receiver)
#     sql = '''INSERT INTO friends (userid1, userid2, status)
#             VALUES (%s, %s, %s)'''
#     values = (sender_id, receiver_id, "pending")
#     data_obj.cursor.execute(sql, values)
#     data_obj.connection.commit()
#     logger.info(f"Friend request sent from {sender} to {receiver}.")

# def accept_friend_request(sender, receiver):
#     sender_id = data_obj.get_id_by_name(sender)
#     receiver_id = data_obj.get_id_by_name(receiver)
#     sql = '''UPDATE friends SET status = %s
#             WHERE userid1 = %s AND userid2 = %s AND status=%s OR
#             userid1 = %s AND userid2 = %s AND status=%s'''
#     values = ("accepted", sender_id, receiver_id, "pending", receiver_id, sender_id, "pending")
#     data_obj.cursor.execute(sql, values)
#     data_obj.connection.commit()
#     logger.info(f"Friend request accepted between {sender} and {receiver}.")

# def reject_friend_request(sender, receiver):
#     sender_id = data_obj.get_id_by_name(sender)
#     receiver_id = data_obj.get_id_by_name(receiver)
#     sql = '''UPDATE friends SET status = %s
#             WHERE userid1 = %s AND userid2 = %s AND status=%s OR
#             userid1 = %s AND userid2 = %s AND status=%s'''
#     values = ("rejected", sender_id, receiver_id, "pending", receiver_id, sender_id, "pending")
#     data_obj.cursor.execute(sql, values)
#     data_obj.connection.commit()
#     logger.info(f"Friend request rejected between {sender} and {receiver}.")
    
# def get_friends(sender):
#     sender_id = data_obj.get_id_by_name(sender)
#     sql = '''SELECT userid1, userid2 FROM friends
#             WHERE (userid1 = %s OR userid2 = %s) AND status = %s'''
#     values = (sender_id, sender_id, "accepted")
#     data_obj.cursor.execute(sql, values)

#     friends = []
#     for row in data_obj.cursor.fetchall():
#         friend_id = row[0] if row[0] != sender_id else row[1]
#         friends.append(data_obj.get_name_by_id(friend_id))
        
#     logger.debug(f"Retrieved friends list for {sender}.")
#     return friends
    
# def remove_friend(sender, receiver):
#     sender_id = data_obj.get_id_by_name(sender)
#     receiver_id = data_obj.get_id_by_name(receiver)
#     sql = '''DELETE FROM friends
#             WHERE (userid1 = %s AND userid2 = %s) OR (userid1 = %s AND userid2 = %s)'''
#     values = (sender_id, receiver_id, receiver_id, sender_id)
#     data_obj.cursor.execute(sql, values)
#     data_obj.connection.commit()
#     logger.info(f"Friendship removed between {sender} and {receiver}.")

def create_chat(members, chat_name):
    chat_id = chats.create_chat()
    sql = '''INSERT INTO chats(name, chat_member_ids, chat_content_id) VALUES (%s, %s, %s)'''
    members_json = json.dumps(members)
    values = (chat_name, members_json, chat_id)
    data_obj.cursor.execute(sql, values)
    data_obj.connection.commit()
    logger.info(f"Chat created with id {chat_id}")
    return "Successful"

def get_chats(userid): # return chat_document_id, chat_name, member_id_list
    sql = '''SELECT chat_content_id, name FROM chats WHERE JSON_CONTAINS(chat_member_ids, %s)'''
    values = (json.dumps([userid]),)
    data_obj.cursor.execute(sql, values)
    result = data_obj.cursor.fetchall()

    formatted_results = []

    for chat_content_id, chat_name in result:
        formatted_results.append({
            "chat_id": chat_content_id,
            "chat_name": chat_name
        })

    return formatted_results