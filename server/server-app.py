from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import Database
import bcrypt

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

db = Database()
clients = {}  # Active users {socket_id: username}

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()

    if db.add_user(username, password):
        return jsonify({"success": True, "message": "User registered"})
    return jsonify({"success": False, "message": "Username already exists"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data["username"], data["password"]
    
    if db.verify_user(username, password):
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid credentials"})

@socketio.on("connect")
def handle_connect():
    print("New client connected:", request.sid)

@socketio.on("login")
def handle_login(data):
    username = data["username"]
    clients[request.sid] = username
    db.set_user_status(username, "online")
    
    emit("update_users", db.get_online_users(), broadcast=True)

@socketio.on("message")
def handle_message(data):
    username = clients.get(request.sid, "Unknown")
    message = f"[{username}] {data['message']}"
    
    db.save_message(username, data["message"])
    emit("chat_message", {"message": message}, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    username = clients.pop(request.sid, None)
    if username:
        db.set_user_status(username, "offline")
        emit("update_users", db.get_online_users(), broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
