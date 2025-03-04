from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QListWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import socketio

SERVER_URL = "https://wireless-chat-app.onrender.com"
sio = socketio.Client()

class SocketThread(QThread):
    received_message = pyqtSignal(str)
    updated_users = pyqtSignal(list)

    def run(self):
        try:
            sio.connect(SERVER_URL)
            sio.on("chat_message", self.on_message)
            sio.on("update_users", self.on_users)
            sio.wait()  # Keep the socket running
        except Exception as e:
            self.received_message.emit(f"❌ Connection Error: {str(e)}")

    def on_message(self, data):
        self.received_message.emit(data["message"])

    def on_users(self, users):
        self.updated_users.emit(users)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Chat")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)
        layout.addWidget(self.chat_box)

        self.online_users = QListWidget(self)
        layout.addWidget(self.online_users)

        self.msg_entry = QLineEdit(self)
        self.msg_entry.setPlaceholderText("Type your message...")
        layout.addWidget(self.msg_entry)

        send_btn = QPushButton("Send", self)
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)

        self.setLayout(layout)

        # Start SocketIO in a separate thread
        self.socket_thread = SocketThread()
        self.socket_thread.received_message.connect(self.receive_message)
        self.socket_thread.updated_users.connect(self.update_users)
        self.socket_thread.start()

    def send_message(self):
        message = self.msg_entry.text().strip()
        if message:
            sio.emit("message", {"message": message})
            self.msg_entry.clear()

    def receive_message(self, message):
        self.chat_box.append(message)

    def update_users(self, users):
        self.online_users.clear()
        self.online_users.addItems(users)

app = QApplication([])
window = ChatWindow()
window.show()
app.exec_()
