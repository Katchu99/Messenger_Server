####LIBRARY IMPORTS####
import json
import logging
from db import mongo_obj

##INITIALIZE LOGGING##
logger = logging.getLogger(__name__)

##SET UP DATABASE CONNECTION##
mongo_db = mongo_obj.mongo_db


def create_chat_mySQL(members, chat_name):
    chat_id = create_chat_mongodb()
    sql = '''INSERT INTO chats(name, chat_member_ids, chat_content_id) VALUES (%s, %s, %s)'''
    members_json = json.dumps(members)
    values = (chat_name, members_json, chat_id)
    data_obj.cursor.execute(sql, values)
    data_obj.connection.commit()
    logger.info(f"Chat created with id {chat_id}")
    return "Successful"


def create_chat_mongodb():
    chat_data = {
        "messages": [
        ]
    }    
    if mongo_db is None:
        print("MongoDB connection not initialized!")
        return

    collection = mongo_db['chat_content']
    chat_id = collection.insert_one(chat_data).inserted_id
    return str(chat_id)


def create_chat(members, chat_name):
    chat_id = create_chat_mongodb()
    create_chat_mySQL(chat_id, members, chat_name)

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