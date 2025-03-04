from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from database import Database
import bcrypt

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow WebSocket connections

# Initialize Database
db = Database()
clients = {}  # Active users {socket_id: username}

# ✅ Default Route to Check if Server is Running
@app.route("/")
def home():
    return "Flask-SocketIO Server is Running!"

# ✅ User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    if db.add_user(username, hashed_password):
        return jsonify({"success": True, "message": "User registered"}), 201
    return jsonify({"success": False, "message": "Username already exists"}), 409

# ✅ User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if db.verify_user(username, password):
        return jsonify({"success": True, "message": "Login successful"}), 200
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ✅ WebSocket Connection
@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")

# ✅ WebSocket Login
@socketio.on("login")
def handle_login(data):
    username = data.get("username")
    
    if not username:
        return
    
    clients[request.sid] = username
    db.set_user_status(username, "online")
    
    emit("update_users", db.get_online_users(), broadcast=True)
    print(f"{username} logged in.")

# ✅ Handle Chat Messages
@socketio.on("message")
def handle_message(data):
    username = clients.get(request.sid, "Unknown")
    message = f"[{username}] {data.get('message', '')}"
    
    db.save_message(username, data["message"])
    emit("chat_message", {"message": message}, broadcast=True)
    print(f"Message received: {message}")

# ✅ Handle Client Disconnect
@socketio.on("disconnect")
def handle_disconnect():
    username = clients.pop(request.sid, None)
    if username:
        db.set_user_status(username, "offline")
        emit("update_users", db.get_online_users(), broadcast=True)
        print(f"{username} disconnected.")

# ✅ Run the Flask-SocketIO Server
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
