from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
import socketio

class SocketThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()

        @self.sio.on("chat_message")
        def on_message(data):
            self.message_received.emit(data["message"])

    def run(self):
        self.sio.connect("https://wireless-chat-app.onrender.com")

    def send_message(self, message):
        self.sio.emit("message", {"message": message})

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat App")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.input_box = QLineEdit(self)
        self.layout.addWidget(self.input_box)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

        self.socket_thread = SocketThread()
        self.socket_thread.message_received.connect(self.update_chat)
        self.socket_thread.start()

    def send_message(self):
        message = self.input_box.text()
        if message:
            self.socket_thread.send_message(message)
            self.input_box.clear()

    def update_chat(self, message):
        self.chat_display.append(message)

if __name__ == "__main__":
    app = QApplication([])
    window = ChatApp()
    window.show()
    app.exec_()
