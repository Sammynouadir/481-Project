import tkinter as tk
import socket
import json
import threading

#assign variables in command prompt
import sys

if len(sys.argv) != 3:
    print("Syntax: python script.py <PORT> <LISTENING_KEY>")
    sys.exit(1)

CURRENT_PORT = sys.argv[1]
listeningFor = sys.argv[2]

def sendUDP(data):
    json_message = json.dumps(data)
    server_socket.sendto(json_message.encode(), (SERVER_IP, int(SERVER_PORT)))

def listen():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_socket.bind((SERVER_IP, int(CURRENT_PORT)))  

    while True:
        message, address = listen_socket.recvfrom(1024)
        try:
            data = json.loads(message.decode())

            if "Reset" in data and data["Reset"] == 1:
#                print(data)
                reset_valve_control()  
            elif listeningFor in data:
#                print(f"Received update: {data[listeningFor]}")
                app.update_lights(int(data[listeningFor] * 5))  #
                
        except Exception as e:            
            print("Error: ", e)

def reset_valve_control():
    app.reset_lights()

class LightControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Valve Control " + listeningFor)
        self.root.minsize(400, 200)

        self.canvas = tk.Canvas(root, bg="light grey")
        self.canvas.pack(fill="both", expand=True)

        self.lights = []
        self.light_status = [False] * 5  # Track on/off state of lights
        
        self.create_lights()
        self.create_triangles()

    def create_lights(self):
        self.lights = []
        start_x = 100
        for i in range(5):
            x = start_x + i * 40
            light = self.canvas.create_oval(x, 50, x + 30, 80, fill="gray", outline="black")
            self.lights.append(light)

    def create_triangles(self):
        # Left Triangle (Decrease)
        self.left_triangle = self.canvas.create_polygon(50, 100, 30, 120, 50, 140, fill="red")
        self.canvas.tag_bind(self.left_triangle, "<Button-1>", self.send_decrease)

        # Right triangle (Increase)
        self.right_triangle = self.canvas.create_polygon(350, 100, 370, 120, 350, 140, fill="green")
        self.canvas.tag_bind(self.right_triangle, "<Button-1>", self.send_increase)

    def send_increase(self, event=None):
        data = {"valve controller increment": 1}
        sendUDP(data)

    def send_decrease(self, event=None):
        data = {"valve controller decrement": 1}
        sendUDP(data)

    def update_lights(self, value):
        colors = ["red", "red", "yellow", "green", "green"]

        #reset all lights
        self.light_status = [False] * 5
        for i in range(5):
            self.canvas.itemconfig(self.lights[i], fill="gray")

        # turn on lights based on received value from pump brain
        for i in range(min(value, 5)):  # out of bounds handling
            self.canvas.itemconfig(self.lights[i], fill=colors[i])
            self.light_status[i] = True

    def reset_lights(self):
        """Resets all lights to off."""
        self.light_status = [False] * 5
        for light in self.lights:
            self.canvas.itemconfig(light, fill="gray")


print(CURRENT_PORT, " ", listeningFor)

SERVER_PORT = 8150
SERVER_IP = "127.0.0.1"

#initialize UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# start Tkinter GUI
root = tk.Tk()
app = LightControlApp(root)

#start listening thread
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

#Start GUI
root.mainloop()

# Close socket when program ends
server_socket.close()
