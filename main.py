from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin
from server_db import chatDB


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
db = chatDB(host="localhost", user="server", password="rootroot", database="mawi")

#messages = []
connections = {}

# Route for login
# TODO muss userdata zurückgeben
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() # User data from request
    print(data)
    # check if username and password exist and are correct
    if db.check_if_exists(data['username']):
        if db.authenticate_user(data['username'], data['password']):
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Login failed'})
    else:
        return jsonify({'success': False, 'message': 'User does not exist'})

# Route for register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() # User data from request
    if db.check_if_exists(data['username']):
        return jsonify({'success': False, 'message': 'Username already taken'}), 401
    else:
        db.register_user(data['username'], data['password'])
        return jsonify({'success': True, 'message': 'Register successful'})

# Route for receiving messages via HTTP POST
@app.route('/messages', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def receive_messages():
    data = request.get_json()
    message = {
        'username': data['username'],
        'text': data['text']
    }
    #messages.append(message)
    #Send message to all through WebSocket connected Clients
    socketio.emit('message', message)
    return jsonify({'success': True})

#Route zum Abrufen von Nachrichten über HTTP GET
@app.route('/messages', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_messages():
    return jsonify(db.get_global_message_history())

# WebSocket-Event-Handler to receive messages
@socketio.on('message')
def handle_message(message):
    # Safe message, will be replaced with db connection
    #messages.append(message)
    send(message, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="localhost", port=6969)