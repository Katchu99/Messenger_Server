import sys
sys.path.append("..")  # Fügt das übergeordnete Verzeichnis dem Python-Systempfad hinzu

from db.chats import mongo_obj
mongo_db = mongo_obj.mongo_db

def create_chat():
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
