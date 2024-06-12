import sys
sys.path.append("..")  # Fügt das übergeordnete Verzeichnis dem Python-Systempfad hinzu

from index import mongo_obj
mongo_db = mongo_obj.mongo_db


""" chat_data = {
        "messages": [
            {"_id":  ObjectId() ,"userid":"user1", "message": "Hello", "timestamp": "2024-06-09 12:00:00"},
            {"_id":  ObjectId() ,"userid":"user2", "message": "Hi there", "timestamp": "2024-06-09 12:05:00"}
        ]
    }    
insert_chat_to_db(chat_data) """

def insert_chat_to_db():
    chat_data = {
        "messages": [
        ]
    }    
    if mongo_db is None:
        print("MongoDB connection not initialized!")
        return

    collection = mongo_db['chats']
    chat_id = collection.insert_one(chat_data).inserted_id
    return chat_id
