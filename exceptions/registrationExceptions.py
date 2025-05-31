class RegistrationException(Exception):
    #Base class for registartion-related exceptions
    pass

class UserAlreadyExists(RegistrationException):
    #Raised when attempting to register a username that already exists
    pass

class EmailAlreadyExists(RegistrationException):
    #Raised when attempting to register an email that already exists
    pass

class WeakPasswordError(RegistrationException):
    #Raised when the provided password does not meet security requirements
    pass

class InvalidEmailError(RegistrationException):
    #Raised when the provided email is invalid or malformed
    pass