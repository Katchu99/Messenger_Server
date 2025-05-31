####LIBRARY IMPORTS####
import re
import bcrypt
import logging
import datetime
from flask_jwt_extended import create_access_token, create_refresh_token

##INITIALIZE LOGGING##
logger = logging.getLogger(__name__)

####EXCEPTION IMPORTS####
from exceptions.registrationExceptions import WeakPasswordError

def validate_password_strength(password: str):
    """
    Checks if the password meets security requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (e.g., !@#$%^&*)

    Exceptions:
        WeakPasswordError: If password doesnt meet security requirements. (exceptions.registrationException)
    """

    checks = [
        (len(password) >= 8, "Password must be at least 8 characters long"),
        (re.search(r"[A-Z]", password), "Password must contain an uppercase letter"),
        (re.search(r"[a-z]", password), "Password must contain a lowercase letter"),
        (re.search(r"\d", password), "Password must contain a number"),
        (re.search(r"[!@#$%^&*(),.?\":{}|<>]", password), "Password must contain a special character")
    ]

    for valid, error_msg in checks:
        if not valid:
            raise WeakPasswordError(error_msg)
        
def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def create_tokens(identity: dict, remember_me: bool) -> tuple[str, str]:
    ##TOKEN EXPIRATION##
    access_expires = datetime.timedelta(minutes=60)

    if remember_me:
        refresh_expires = datetime.timedelta(days=14)
    else:
        refresh_expires = datetime.timedelta(days=1)

    ##GENERATE TOKEN##
    access_token = create_access_token(identity=identity, expires_delta=access_expires)
    refresh_token = create_refresh_token(identity=identity, expires_delta=refresh_expires)

    return tuple[access_token, refresh_token]