import datetime
from pymongoose import methods
from pymongoose.mongo_types import Types, Schema, MongoException, MongoError
from bson import json_util
from bson.objectid import ObjectId

class Chat(Schema):
    schema_name = "chats" # Name of the schema that mongo uses
    
    # Attributes
    id = None
    name = None
    messages = None

    def __init__(self, **kwargs):
        self.schema = {
            "messages": {
                "type": list,
                "required": False,
                "schema": {
                    "type": dict,
                    "schema": {
                        "_id": {"type": ObjectId, "required": True},
                        "userid": {"type": str, "required": True},
                        "message": {"type": str, "required": True},
                        "timestamp": {"type": str, "required": True}
                    }
                }
            }
        }

        super().__init__(self.schema_name, self.schema, kwargs)

    def __str__(self):
        return f"Role: {self.name}, Actions: {self.action}"