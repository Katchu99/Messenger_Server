####LIBRARY IMPORTS####
import logging
import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token

####LOCAL IMPORTS####
from database.controllers.auth import register_user, authenticate_user
from utils.db_utils import get_id_by_name
from utils.helper_utils import validate_password_strength, hash_password

####EXCEPTION IMPORTS####
from exceptions.authenticationExceptions import UserNotFoundError, InvalidPasswordError
from exceptions.registrationExceptions import UserAlreadyExists,EmailAlreadyExists, WeakPasswordError

auth_routes = Blueprint('auth_routes', __name__)

logger = logging.getLogger(__name__)

### ROUTE: LOGIN ###
@auth_routes.route('/login', methods=['POST'])
def login():
    login_request = request.get_json() # User data from request

    logger.info('Login attempt for user: %s', login_request['username'])

    username = login_request['username']
    password = login_request['password']

    try:
        authenticate_user(username=username, password=password)  # Will throw UserNotFoundError or InvalidPasswordError if authentication failed.

        ##TOKEN EXPIRATION##
        access_expires = datetime.timedelta(minutes=30)
        remember_me = login_request.get('remember_me', False)

        if remember_me:
            refresh_expires = datetime.timedelta(days=14)
        
        else:
            refresh_expires = datetime.timedelta(days=1)
    
        ##SET TOKEN DATA##
        user_id = get_id_by_name(username)
        identity = {'id': str(user_id), 'username': username}

        ##GENERATE TOKEN##
        access_token = create_access_token(identity=identity, expires_delta=access_expires)
        refresh_token = create_refresh_token(identity=identity, expires_delta=refresh_expires)

        ##SET RESPONSE##
        response = jsonify({'success': True, 'message': 'Authentication successful', 'user':identity})
        response.set_cookie('access_token',access_token, secure=True, httponly=True)
        response.set_cookie('refresh_token',refresh_token, secure=True, httponly=True)

        logger.info(f"User {username} successfully authenticated.")
        return response


    except (UserNotFoundError, InvalidPasswordError) as err:
        logger.warning(f'Failed authentication for {username}: {err}')
        return jsonify({'success': False, 'message': "Authentication failed"}), 401

    except Exception as err:
        logger.warning(f'Unexpected error at authentication for {username}: {err}')
        return jsonify({'success': False, 'message': "Authentication failed"}), 401
    

### ROUTE: REGISTER ###
@auth_routes.route('/register', methods=['POST'])
def register():
    register_request = request.get_json() # User data from request

    logger.info('Registration attempt for user: %s', register_request['username'])

    username = register_request['username']
    password = register_request['password']
    email = register_request.get('email')

    if not email:
        logger.warning(f'Registration failed for {username}: Email is required')
        return jsonify({'success': False, 'message': "Email is required"}), 400
    if not username:
        logger.warning(f'Registration failed for {username}: Username is required')
        return jsonify({'success': False, 'message': "Username is required"}), 400
    if not password:
        logger.warning(f'Registration failed for {username}: Password is required')
        return jsonify({'success': False, 'message': "Password is required"}), 400

    try:
        validate_password_strength(password)
        hash_pw = hash_password(password)  # Uncomment if hashing is needed
        register_user(username=username, email=email, password=hash_pw)

        return jsonify({'success': True, 'message': "Registration successful"}), 201
    
    except WeakPasswordError as err:
        logger.warning(f'Registration failed for {username}: {err}')
        return jsonify({'success': False, 'message': str(err)}), 400

    except UserAlreadyExists as err:
        logger.warning(f'Registration failed for {username}: {err}')
        return jsonify({'success': False, 'message': "Username already taken"}), 400

    except EmailAlreadyExists as err:
        logger.warning(f'Registration failed for {username}: {err}')
        return jsonify({'success': False, 'message': "Email already taken"}), 400

    except Exception as err:    
        logger.warning(f'Registration failed for {username}: {err}')
        return jsonify({'success': False, 'message': "Registration failed"}), 500