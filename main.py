from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
socketio = SocketIO(app)

messages = []

# Route for receiving messages via HTTP POST
@app.route('/messages', methods=['POST'])
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