import tkinter as tk
from tkinter import scrolledtext
import socketio
from tkinter import messagebox

# Initialize SocketIO client
sio = socketio.Client()

# Connect to server
try:
    sio.connect("https://wireless-chat-app.onrender.com")  # Change to live server when deploying
    connected = True
except:
    connected = False
    messagebox.showerror("Connection Error", "Could not connect to the server.")

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wireless Chat")
        self.root.geometry("500x600")
        self.root.configure(bg="#282c34")

        # Header Label
        self.header = tk.Label(root, text="Wireless Chat", font=("Arial", 16, "bold"), bg="#61afef", fg="white", pady=5)
        self.header.pack(fill=tk.X)

        # Status Bar
        self.status = tk.Label(root, text="Connected" if connected else "Disconnected", font=("Arial", 10), bg="#98c379", fg="black")
        self.status.pack(fill=tk.X)

        # User List Panel
        self.user_list_frame = tk.Frame(root, bg="#3e4451", width=150)
        self.user_list_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_list_label = tk.Label(self.user_list_frame, text="Online Users", font=("Arial", 12, "bold"), fg="white", bg="#3e4451")
        self.user_list_label.pack(pady=5)

        self.user_list = tk.Listbox(self.user_list_frame, bg="#282c34", fg="white")
        self.user_list.pack(fill=tk.BOTH, expand=True)

        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(root, state="disabled", wrap=tk.WORD, bg="#1e2127", fg="white", font=("Arial", 12))
        self.chat_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Bottom Panel
        self.bottom_frame = tk.Frame(root, bg="#282c34")
        self.bottom_frame.pack(fill=tk.X, pady=5)

        self.message_input = tk.Entry(self.bottom_frame, font=("Arial", 12), bg="#3e4451", fg="white", width=40)
        self.message_input.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.message_input.bind("<Return>", self.send_message)  # Send on Enter key press

        self.send_button = tk.Button(self.bottom_frame, text="Send", command=self.send_message, bg="#61afef", fg="white", font=("Arial", 12, "bold"))
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # Listen for messages & users
        sio.on("message", self.receive_message)
        sio.on("user_list", self.update_users)

    def send_message(self, event=None):
        message = self.message_input.get()
        if message:
            sio.emit("message", {"user": "You", "msg": message})
            self.message_input.delete(0, tk.END)

    def receive_message(self, data):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{data['user']}: {data['msg']}\n", "user" if data['user'] == "You" else "other")
        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)  # Auto-scroll

    def update_users(self, users):
        self.user_list.delete(0, tk.END)
        for user in users:
            self.user_list.insert(tk.END, user)

# Run the application
root = tk.Tk()
app = ChatApp(root)
root.mainloop()

