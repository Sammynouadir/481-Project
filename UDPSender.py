import socket
import json
from tkinter import Tk, Label, Entry, Button, messagebox, N, S, E, W
from threading import Timer

class UdpMessageApp:
    def __init__(self, root):
        # Initialize the root window
        self.root = root
        self.root.title("UDP Message Sender")
        
        # Configure grid resizing weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Text Fields
        Label(root, text="Key:").grid(row=0, column=0, padx=10, pady=5, sticky=E)
        self.key_field = Entry(root)
        self.key_field.grid(row=0, column=1, padx=10, pady=5, sticky=E+W)

        Label(root, text="Value:").grid(row=1, column=0, padx=10, pady=5, sticky=E)
        self.value_field = Entry(root)
        self.value_field.grid(row=1, column=1, padx=10, pady=5, sticky=E+W)
        
        Label(root, text="Port:").grid(row=2, column=0, padx=10, pady=5, sticky=E)
        self.port_field = Entry(root)
        self.port_field.grid(row=2, column=1, padx=10, pady=5, sticky=E+W)
        
        # Buttons
        self.start_button = Button(root, text="Start", command=self.start_timer)
        self.start_button.grid(row=3, column=0, pady=10, sticky=E+W)
        
        self.pause_button = Button(root, text="Pause", command=self.pause_timer)
        self.pause_button.grid(row=3, column=1, pady=10, sticky=E+W)

        # Message counter
        Label(root, text="Messages Sent:").grid(row=4, column=0, padx=10, pady=5, sticky=E)
        self.counter_label = Label(root, text="0")
        self.counter_label.grid(row=4, column=1, padx=10, pady=5, sticky=E+W)
        self.message_count = 0  # Counter variable
        
        # Initialize UDP client
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timer = None 
        self.is_sending = False

    def send_message(self):
        # Get input values
        key = self.key_field.get()
        value = self.value_field.get()
        port = self.port_field.get()

        # Validate input
        if not key or not value or not port:
            self.show_error("All fields must be filled out!")
            return
        
        try:
            port = int(port)
        except ValueError:
            self.show_error("The port must be an integer!")
            return
        
        try:
            value = float(value)
        except ValueError:
            self.show_error("The value must be a number!")
            return

        # Serialize to JSON
        data = [{"Key": key, "Value": value}]
        json_data = json.dumps(data)

        # Send JSON over UDP
        try:
            self.udp_socket.sendto(json_data.encode('utf-8'), ("127.0.0.1", port))
            self.update_counter()
        except Exception as e:
            self.show_error(f"Failed to send data: {e}")

    def update_counter(self):
        # Increment and display the message count
        self.message_count += 1
        self.counter_label.config(text=str(self.message_count))

    def start_timer(self):
        if not self.is_sending:
            self.is_sending = True
            self.schedule_timer()

    def pause_timer(self):
        self.is_sending = False
        if self.timer:
            self.timer.cancel()

    def schedule_timer(self):
        if self.is_sending:
            self.timer = Timer(0.05, self.timer_callback)
            self.timer.start()

    def timer_callback(self):
        self.send_message()
        self.schedule_timer()

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def on_close(self):
        self.pause_timer()
        self.udp_socket.close()
        self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = Tk()
    app = UdpMessageApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
