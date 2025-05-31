import datetime
from pymongoose import methods
from pymongoose.mongo_types import Types, Schema, MongoException, MongoError
from bson import json_util
from bson.objectid import ObjectId

class User(Schema):
    schema_name = "user" # Name of the schema that mongo uses
    
    # Attributes
    id = None
    username = None
    email = None

    def __init__(self, **kwargs):
        self.schema = {
            "_id": {"type": ObjectId, "required": True},
            "username": {"type": str, "required": True},
            "email": {"type": str, "required": True},
            "profile_pic": {"type": str, "required": False},
            "createdAt": {"type": datetime.datetime, "required": True, "default": datetime.datetime.now},
        }

        super().__init__(self.schema_name, self.schema, kwargs)

    def __str__(self):
        return f"Role: {self.name}, Actions: {self.action}"
