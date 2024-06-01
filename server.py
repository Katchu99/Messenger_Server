import logging
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin
from server_db import chatDB

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
logger.info("Establishing DB connection...")
db = chatDB(host="localhost", user="server", password="rootroot", database="mawi")

#messages = []
connections = {}

# Route for login
# TODO muss userdata zurückgeben
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() # User data from request
    logger.info('Login attempt for user: %s', data['username'])

    # check if username and password exist and are correct
    if db.check_if_exists(data['username']):
        if db.authenticate_user(data['username'], data['password']):
            logger.info('Login successful for user: %s', data['username'])
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            logger.warning('Login failed for user: %s', data['username'])
            return jsonify({'success': False, 'message': 'Login failed'})
    else:
        logger.warning('User does not exist: %s', data['username'])
        return jsonify({'success': False, 'message': 'User does not exist'})

# Route for register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() # User data from request
    logger.info('Registration attempt for user: %s', data['username'])

    if db.check_if_exists(data['username']):
        logger.warning('Registration failed - Username already taken: %s', data['username'])
        return jsonify({'success': False, 'message': 'Username already taken'}), 400
    else:
        db.register_user(data['username'], data['password'])
        logger.info('Registration successful for user: %s', data['username'])
        return jsonify({'success': True, 'message': 'Register successful'})

# Route for receiving messages via HTTP POST
#@app.route('/messages', methods=['POST'])
#@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
#def receive_messages():
#    data = request.get_json()
#    message = {
#        'username': data['username'],
#        'text': data['text']
#    }
#
#    # for development reasons only, remove going into production mode
#    print(message)
#
#    #messages.append(message)
#    #Send message to all through WebSocket connected Clients
#    socketio.emit('message', message)
#    return jsonify({'success': True})

#Route zum Abrufen von Nachrichten über HTTP GET
@app.route('/messages', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_messages():
    return jsonify(db.get_global_message_history())

# WebSocket-Event-Handler to receive messages
@socketio.on('message')
def handle_message(message):
    logger.info('Received message: %s', message)
    # Safe message, will be replaced with db connection
    #messages.append(message)
    send(message, broadcast=True)

if __name__ == "__main__":
    #ssl_context = ('./SSL/localhost.pem', './SSL/localhost-key.pem')
    socketio.run(app, host="localhost", port=6969) #, ssl_context=ssl_context)
    logger.info("Server running.")