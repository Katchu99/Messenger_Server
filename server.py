import logging
import datetime
import secrets
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin

import db.controller.data as data

# Initialize Logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='server.log',
    filemode='w'
)

# Adding console handler
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Initialzie Logger for this Module
logger = logging.getLogger(__name__)

logger.info("Initializing Flask App...")
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
logger.info("Establishing data connection...")

connections = {}

# Generate Random Key
def generate_secret_key(length=32):
    return secrets.token_hex(length)

# JWT Secret and Manage
app.config['JWT_SECRET_KEY'] = generate_secret_key()
jwt = JWTManager(app)

# Route for login
# TODO muss userdata zurückgeben
@app.route('/login', methods=['POST'])
def login():
    login_request = request.get_json() # User data from request
    logger.info('Login attempt for user: %s', login_request['username'])
    username = login_request['username']
    # check if username and password exist and are correct
    if data.check_if_exists(username):
        if data.authenticate_user(username, login_request['password']):
            logger.info('Login successful for user: %s', username)

            access_expires = datetime.timedelta(minutes=30)
            # Set Refresh-Token expire time based on remember_me
            remember_me = login_request.get('remember_me', False)
            if remember_me:
                refresh_expires = datetime.timedelta(days=14)
            else:
                refresh_expires = datetime.timedelta(days=1)

            # Generate the JWT-Token
            user_id = data.get_id_by_name(username)
            identity = {'id': user_id, 'username': username}
            access_token = create_access_token(identity=identity, expires_delta=access_expires)
            refresh_token = create_access_token(expires_delta=refresh_expires)

            print(identity)
            response = jsonify({'success': True, 'message': 'Login successful', 'user': identity})
            response.set_cookie('access_token', access_token, secure=True, httponly=True)
            response.set_cookie('refresh_token', refresh_token, secure=True, httponly=True)
            return response
        
        else:
            logger.warning('Login failed for user: %s', login_request['username'])
            return jsonify({'success': False, 'message': 'Login failed'})
    else:
        logger.warning('User does not exist: %s', login_request['username'])
        return jsonify({'success': False, 'message': 'User does not exist'})

@app.route('/protected', methods=['GET'])
@jwt_required(refresh=True)
def protected():
    # current_user = get_jwt_identity()
    # return jsonify(logged_in_as=current_user), 200
    identity = get_jwt_identity()
    user_id = identity['id']
    username = identity['username']

    user = {
        'id': user_id,
        'username': username
    }
    return jsonify({'isAuthenticated': True, 'user': user}), 200

# Route for register
@app.route('/register', methods=['POST'])
def register():
    register_request = request.get_json() # User data from request
    logger.info('Registration attempt for user: %s', register_request['username'])
    

    if data.check_if_exists(register_request['username']):
        logger.warning('Registration failed - Username already taken: %s', register_request['username'])
        return jsonify({'success': False, 'message': 'Username already taken'}), 400
    else:
        data.register_user(register_request['username'], register_request['password'])
        logger.info('Registration successful for user: %s', register_request['username'])
        return jsonify({'success': True, 'message': 'Register successful'})


# Route to check auth
@app.route('/check-auth', methods=['GET'])
@jwt_required(refresh=True)
def check_auth():
    identity = get_jwt_identity()
    user_id = identity['id']
    username = identity['username']

    user = {
        'id': user_id,
        'username': username
    }
    return jsonify({'isAuthenticated': True, 'user': user})
    

#Route zum Abrufen von Nachrichten über HTTP GET
@app.route('/chat/<user_uuid>', methods=['GET'])
@jwt_required(refresh=True)
@cross_origin( origins='*', headers=['Content-Type', 'Authorization'])
def get_chats(user_uuid):
    return jsonify(data.get_chats(user_uuid)) #data.get_chats() returns a list of tuples

@app.route('/chat/<user_uuid>/createChat', methods=['POST'])
@jwt_required(refresh=True)
@cross_origin(origins='*', headers=['Content-Type', 'Authorization'])
def createChat(user_uuid):
    createChatRequest = request.get_json()
    members = createChatRequest['members']
    chatName = createChatRequest['name']
    if data.create_chat(members, chatName) == "Successful":
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    


# WebSocket-Event-Handler to receive messages
@socketio.on('message')
def handle_message(message):
    logger.info('Received message: %s', message)
    send(message, broadcast=True)

if __name__ == "__main__":
    #ssl_context = ('./SSL/localhost.pem', './SSL/localhost-key.pem')
    socketio.run(app, host="localhost", port=5000) #, ssl_context=ssl_context)