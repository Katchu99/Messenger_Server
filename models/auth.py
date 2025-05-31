from pymongoose.mongo_types import Schema


class Auth(Schema):
    schema_name = "auth" # Name of the schema that mongo uses
    
    # Attributes
    id = None
    username = None
    password = None

    def __init__(self, **kwargs):
        self.schema = {
            "username": {"type": str, "required": True},
            "password": {"type": str, "required": True},
        }

        super().__init__(self.schema_name, self.schema, kwargs)

    def __str__(self):
        return f"Role: {self.name}, Actions: {self.action}"