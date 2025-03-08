import pythonnet
pythonnet.load("coreclr")
import clr
from System.Collections.Generic import Dictionary
import socket
from tkinter import Tk, Label, Entry, Button, Text, Frame, messagebox, N, S, E, W
from threading import Timer

# Add reference to the C# .dll
clr.AddReference("PumpBrain")

# Import the namespace
from PumpBrain import PumpBrain

class UdpMessageApp:
    def __init__(self, root):
        # Create an object of the C# PumpBrain class
        self.pump_brain = PumpBrain()
        
        # Initialize the root window
        self.root = root
        self.root.title("UDP Message Tester")
        
        # Configure grid resizing weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # --- Sending Section ---
        sending_frame = Frame(root, borderwidth=2, relief="groove")
        sending_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=N+S+E+W)
        sending_frame.grid_columnconfigure(0, weight=1)
        sending_frame.grid_columnconfigure(1, weight=1)
        
        Label(sending_frame, text="Send some KvP", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        # Key-Value Pairs 1
        Label(sending_frame, text="Key 1:").grid(row=1, column=0, padx=10, pady=5, sticky=E)
        self.key1_field = Entry(sending_frame)
        self.key1_field.grid(row=1, column=1, padx=10, pady=5, sticky=E+W)
        self.key1_field.insert(0, "tank to pump position")

        Label(sending_frame, text="Value 1:").grid(row=2, column=0, padx=10, pady=5, sticky=E)
        self.value1_field = Entry(sending_frame)
        self.value1_field.grid(row=2, column=1, padx=10, pady=5, sticky=E+W)
        self.value1_field.insert(0, "1.0")

        # Key-Value Pairs 2
        Label(sending_frame, text="Key 2:").grid(row=3, column=0, padx=10, pady=5, sticky=E)
        self.key2_field = Entry(sending_frame)
        self.key2_field.grid(row=3, column=1, padx=10, pady=5, sticky=E+W)
        self.key2_field.insert(0, "pto")

        Label(sending_frame, text="Value 2:").grid(row=4, column=0, padx=10, pady=5, sticky=E)
        self.value2_field = Entry(sending_frame)
        self.value2_field.grid(row=4, column=1, padx=10, pady=5, sticky=E+W)
        self.value2_field.insert(0, "1.0")

        # Key-Value Pairs 3
        Label(sending_frame, text="Key 3:").grid(row=5, column=0, padx=10, pady=5, sticky=E)
        self.key3_field = Entry(sending_frame)
        self.key3_field.grid(row=5, column=1, padx=10, pady=5, sticky=E+W)
        self.key3_field.insert(0, "tank fill position")

        Label(sending_frame, text="Value 3:").grid(row=6, column=0, padx=10, pady=5, sticky=E)
        self.value3_field = Entry(sending_frame)
        self.value3_field.grid(row=6, column=1, padx=10, pady=5, sticky=E+W)
        self.value3_field.insert(0, "0.0")

        # Send Port Field
        Label(sending_frame, text="Send Port:").grid(row=7, column=0, padx=10, pady=5, sticky=E)
        self.port_field = Entry(sending_frame)
        self.port_field.grid(row=7, column=1, padx=10, pady=5, sticky=E+W)
        self.port_field.insert(0, "8150")
        
        # Buttons
        self.start_button = Button(sending_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=8, column=0, pady=10, sticky=E+W)
        
        self.pause_button = Button(sending_frame, text="Pause", command=self.pause_timer)
        self.pause_button.grid(row=8, column=1, pady=10, sticky=E+W)

        # Message counter
        Label(sending_frame, text="Messages Sent:").grid(row=9, column=0, padx=10, pady=5, sticky=E)
        self.counter_label = Label(sending_frame, text="0")
        self.counter_label.grid(row=9, column=1, padx=10, pady=5, sticky=E+W)
        self.message_count = 0  # Counter variable
        
        # --- Incoming Data Section ---
        incoming_frame = Frame(root, borderwidth=2, relief="groove")
        incoming_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=N+S+E+W)
        incoming_frame.grid_columnconfigure(0, weight=1)
        incoming_frame.grid_columnconfigure(1, weight=1)
        
        Label(incoming_frame, text="Listening on port 8150", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        Label(incoming_frame, text="Latest Message Received:", font=("Arial", 12, "bold")).grid(row=1, column=0, columnspan=2, pady=5)

        # Expandable Text Box for Latest Message
        self.latest_message_text = Text(incoming_frame, wrap="word", height=35, width=60)
        self.latest_message_text.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=N+S+E+W)

        # Messages Received Counter
        Label(incoming_frame, text="Messages Received:").grid(row=3, column=0, padx=10, pady=5, sticky=E)
        self.received_counter_label = Label(incoming_frame, text="0")
        self.received_counter_label.grid(row=3, column=1, padx=10, pady=5, sticky=E+W)
        self.received_message_count = 0  # Counter for messages received

        # Variable to track the last processed message
        self.last_message = None

        # Initialize UDP client
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timer = None 
        self.is_sending = False
        
        # Periodic checker for the latest received message
        self.start_latest_message_checker()



    def send_message(self):
        # Get input values
        keys = [self.key1_field.get(), self.key2_field.get(), self.key3_field.get()]
        values = [self.value1_field.get(), self.value2_field.get(), self.value3_field.get()]
        port = self.port_field.get()

        # Validate required fields
        if not self.key1_field.get() or not self.value1_field.get() or not port:
            self.show_error("Key 1, Value 1, and Port fields are required!")
            return

        # Convert port to an integer
        try:
            port = int(port)
        except ValueError:
            self.show_error("The port must be an integer!")
            return

        # Convert values to float (handling empty strings as 0.0)
        try:
            values = [float(v) if v else 0.0 for v in values]
        except ValueError:
            self.show_error("All values must be numbers!")
            return

        # Create a Python dictionary with key-value pairs
        data = {key: value for key, value in zip(keys, values) if key}

        # Convert Python dictionary to C# Dictionary<string, double>
        csharp_data = Dictionary[str, float]()
        for key, value in data.items():
            csharp_data[key] = float(value)

        try:
            # Call the C# function with the properly formatted dictionary
            self.pump_brain.TestToolSupporter.BackDoorSendTestUDP(csharp_data, port)
            self.update_counter()  # Increment the message count only on success
        except Exception as e:
            self.show_error(f"Failed to send data: {e}")


    def update_counter(self):
        self.message_count += 1  # Increment the count
        self.counter_label.config(text=str(self.message_count))  # Update the label text

    def increment_received_counter(self):
        """Increment the received message counter."""
        self.received_message_count += 1
        self.received_counter_label.config(text=str(self.received_message_count))

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

    def start_latest_message_checker(self):
        """Periodically checks for the latest received message from the C# object."""
        self.check_latest_message()
        self.root.after(50, self.start_latest_message_checker)  # Check every 0.05 seconds

    def check_latest_message(self):
        """Fetch and display the latest received message."""
        try:
            latest_message = self.pump_brain.TestToolSupporter.LatestMessage
            if latest_message != self.last_message:
                # Update the UI with the new message
                display_text = "\n".join([f"{kvp.Key}: {kvp.Value}" for kvp in latest_message])
                self.latest_message_text.delete("1.0", "end")  # Clear the text box
                self.latest_message_text.insert("1.0", display_text)  # Insert new text
                self.last_message = latest_message  # Update the last message
                self.increment_received_counter()  # Increment the received message counter
        except Exception as e:
            self.latest_message_text.delete("1.0", "end")
            self.latest_message_text.insert("1.0", f"Error fetching message: {e}")

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
