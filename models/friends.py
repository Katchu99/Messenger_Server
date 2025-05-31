import datetime
from pymongoose import methods
from pymongoose.mongo_types import Types, Schema, MongoException, MongoError
from bson import json_util
from bson.objectid import ObjectId

class Friends(Schema):
    schema_name = "friends" # Name of the schema that mongo uses
    
    # Attributes
    id = None
    user1 = None
    user2 = None
    status = None
    createdAt = None

    def __init__(self, **kwargs):
        self.schema = {
            "_id": {"type": str, "required": True},
            "name1": {"type": str, "required": True},
            "name2": {"type": str, "required": True},
            "status": {"type": str, "required": True, "enum": ["pending", "accepted", "rejected"]},
            "createdAt": {"type": datetime.datetime, "required": True, "default": datetime.datetime.now}
        }

        super().__init__(self.schema_name, self.schema, kwargs)

    def __str__(self):
        return f"Role: {self.name}, Actions: {self.action}"
