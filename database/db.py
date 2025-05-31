####LIBRARY IMPORTS####
import os, traceback
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongoose.methods import set_schemas

####LOCAL IMPORTS####
from models.auth import Auth
from models.user import User
from models.friends import Friends
from models.blocked import Blocked
from models.chat import Chat


class Database():
    def __init__(self) -> None:
        self.MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://localhost:27017"
        self.mongo_db = None
        self.mongo_init()

    def mongo_init(self):
        try:
            client = MongoClient(self.MONGO_URI)
            print(self.MONGO_URI)
            self.mongo_db = client.mawi
        except ServerSelectionTimeoutError as err:
            print("Could not connect to MongoDB:", err)
            
        try:
            schemas = {
                "auth": Auth(empty=True).schema,
                "user": User(empty=True).schema,
                "friends": Friends(empty=True).schema,
                "blocked": Blocked(empty=True).schema,
                "chats": Chat(empty=True).schema
            }
            set_schemas(self.mongo_db, schemas)

            print("MongoDB Connected!")
        except Exception as err:
            traceback.print_exc()
            print("Error initializing database:", err)
            exit(1) 


mongo_obj = Database()

if __name__ == "__main__":
    pass





