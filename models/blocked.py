import datetime
from pymongoose import methods
from pymongoose.mongo_types import Types, Schema, MongoException, MongoError
from bson import json_util
from bson.objectid import ObjectId

class Blocked(Schema):
    schema_name = "blocked" # Name of the schema that mongo uses
    
    # Attributes
    id = None
    blocker = None
    blocked = None
    reported = None
    createdAt = None

    def __init__(self, **kwargs):
        self.schema = {
            "_id": {"type": str, "required": True},
            "blocker": {"type": str, "required": True},
            "blocked": {"type": str, "required": True},
            "reported": {"type": bool, "required": True, "default": False},
            "createdAt": {"type": datetime.datetime, "required": True, "default": datetime.datetime.now}
        }

        super().__init__(self.schema_name, self.schema, kwargs)

    def __str__(self):
        return f"Role: {self.name}, Actions: {self.action}"
