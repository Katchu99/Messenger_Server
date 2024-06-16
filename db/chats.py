import os, traceback
import signal 
from pymongo import MongoClient
from pymongoose.methods import set_schemas, get_cursor_length
from schemas.chats import Chat
from bson.objectid import ObjectId


class mongoDB():
    def __init__(self) -> None:
        self.MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://localhost:27017"
        self.mongo_db = None
        self.mongo_init()

    def mongo_init(self):
        client = MongoClient(self.MONGO_URI)
        print(self.MONGO_URI)
        self.mongo_db = client.chats  # Setzen Sie mongo_db auf die Datenbank
        try:
            # Now schemas can be set in two ways
            # -> In a dict mode
            schemas = {
                "chats": Chat(empty=True).schema
            }
            set_schemas(self.mongo_db, schemas)

            print("MongoDB Connected!")
        except:
            traceback.print_exc()
            print("Error initializing database")
            exit(1) 


mongo_obj = mongoDB()

if __name__ == "__main__":
    from controller.chats import insert_chat_to_db
    
    insert_chat_to_db()





