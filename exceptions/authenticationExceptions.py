
class AuthenticationException(Exception):
    #Base class for authentication-related exceptions
    pass

class UserNotFoundError(AuthenticationException):
    #Exception raised when a user is not found in the database
    pass

class InvalidPasswordError(AuthenticationException):
    #Exception raised when a password is invalid
    pass

