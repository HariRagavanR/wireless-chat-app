from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QListWidget
import socketio 


SERVER_URL = "https://your-chat-server.onrender.com"
sio = socketio.Client()


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Chat")

        layout = QVBoxLayout()

        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)
        layout.addWidget(self.chat_box)

        self.online_users = QListWidget(self)
        layout.addWidget(self.online_users)

        self.msg_entry = QLineEdit(self)
        layout.addWidget(self.msg_entry)

        send_btn = QPushButton("Send", self)
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)

        self.setLayout(layout)

        sio.on("chat_message", self.receive_message)
        sio.on("update_users", self.update_users)
        sio.connect(SERVER_URL)

    def send_message(self):
        message = self.msg_entry.text()
        sio.emit("message", {"message": message})
        self.msg_entry.clear()

    def receive_message(self, data):
        self.chat_box.append(data["message"])

    def update_users(self, users):
        self.online_users.clear()
        self.online_users.addItems(users)

app = QApplication([])
window = ChatWindow()
window.show()
app.exec_()
