from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin
import bcrypt

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'


messages = []

# Route for login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() # User data from request

    # check if username and password exist and are correct
    #  if ... DB CODE GEDÖNS
    # return jsonify({'success': True, 'message': 'Login successful'})
    # else
    # return jsonify({'success': False, 'message': 'wrong credentials'}), 401

# Route for receiving messages via HTTP POST
@app.route('/messages', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def receive_messages():
    data = request.get_json()
    message = {
        'username': data['username'],
        'text': data['text']
    }
    messages.append(message)
    #Send message to all through WebSocket connected Clients
    socketio.emit('message', message)
    return jsonify({'success': True})

#Route zum Abrufen von Nachrichten über HTTP GET
@app.route('/messages', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_messages():
    return jsonify(messages)

# WebSocket-Event-Handler to receive messages
@socketio.on('message')
def handle_message(message):
    # Safe message, will be replaced with db connection
    messages.append(message)
    send(message, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="localhost", port=6969)