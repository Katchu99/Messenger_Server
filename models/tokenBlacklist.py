import datetime
from pymongoose import methods
from pymongoose.mongo_types import Types, Schema, MongoException, MongoError
from bson import json_util
from bson.objectid import ObjectId

class TokenBlacklist(Schema):
    schema_name = "TokenBlacklist" # Name of the schema that mongo uses
    
    # Attributes
    token = None
    expiresAt = None

    def __init__(self, **kwargs):
        self.schema = {
            "token": {"type": str, "required": True},
            "expiresAt": {"type": datetime.datetime, "required": True},
        }

        super().__init__(self.schema_name, self.schema, kwargs)

    def __str__(self):
        return f"Role: {self.name}, Actions: {self.action}"

    @classmethod
    def create_indexes(cls):
        cls.create_indexes(["expiresAt", 1], expireAfterSeconds=0)