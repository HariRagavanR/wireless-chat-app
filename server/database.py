from pymongo import MongoClient
import bcrypt

class Database:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://wireless-chat-app:Hari%40810@wireless-chat-app.fd8mm.mongodb.net/?appName=mongosh+2.4.0")
        self.db = self.client["chat_app"]
        self.users = self.db["users"]
        self.messages = self.db["messages"]

    def add_user(self, username, password):
        if self.users.find_one({"username": username}):
            return False
        self.users.insert_one({"username": username, "password": password, "status": "offline"})
        return True

    def verify_user(self, username, password):
        user = self.users.find_one({"username": username})
        return user and bcrypt.checkpw(password.encode(), user["password"].encode())

    def set_user_status(self, username, status):
        self.users.update_one({"username": username}, {"$set": {"status": status}})
    
    def get_online_users(self):
        return [user["username"] for user in self.users.find({"status": "online"})]

    def save_message(self, username, message):
        self.messages.insert_one({"username": username, "message": message})
