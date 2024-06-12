import sys
sys.path.append("..")  # Fügt das übergeordnete Verzeichnis dem Python-Systempfad hinzu

from db.chats import mongo_obj
mongo_db = mongo_obj.mongo_db

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
