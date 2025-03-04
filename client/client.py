import sys
import socketio
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

# Background thread for SocketIO
class SocketIOThread(QThread):
    message_received = pyqtSignal(str)

    def run(self):
        self.sio = socketio.Client()

        @self.sio.on('message')
        def on_message(data):
            self.message_received.emit(data)  # Send message to GUI thread

        self.sio.connect('https://wireless-chat-app.onrender.com')  # Replace with your server
        self.sio.wait()  # Keep listening for events

    def send_message(self, msg):
        self.sio.emit('message', msg)

# Main GUI
class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chat Client")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        self.send_button = QPushButton("Send Message", self)
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Start SocketIO in a separate thread
        self.socket_thread = SocketIOThread()
        self.socket_thread.message_received.connect(self.display_message)
        self.socket_thread.start()

    def display_message(self, message):
        self.text_area.append(f"Server: {message}")

    def send_message(self):
        self.socket_thread.send_message("Hello from PyQt!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())
