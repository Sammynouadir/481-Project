import tkinter as tk
import socket
import json
import threading

#assign variables in command prompt
import sys

if len(sys.argv) < 3:
    print("Usage: python script.py <PORT> \"<LISTENING_KEY>\"")
    sys.exit(1)

CURRENT_PORT = sys.argv[1]
listeningFor = " ".join(sys.argv[2:])  #handling for spaces in keys

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
                reset_valve_control()  
            elif listeningFor in data:
                app.update_lights(int(data[listeningFor] * 5))  #
                
        except Exception as e:            
            print("Error: ", e)

def reset_valve_control():
    app.reset_lights()

class LightControlApp:
    def __init__(self, root, strength):
        self.strength = 0.0
        self.root = root
        self.root.title("Valve Control " + listeningFor)

        self.root.resizable(True, True)  #resizable window vertically and horizontally

        self.canvas = tk.Canvas(root, bg="light grey")
        self.canvas.pack(fill="both", expand=True)
        self.lights = []
        self.light_status = [False] * 5  # tracks on/off state of lights
        
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
        # Adjust the y-coordinate to align with the lights
        light_y_center = 65  # Approximate vertical center of the lights

        # decrease triangle left side
        self.left_triangle = self.canvas.create_polygon(50, light_y_center - 15, 
                                                    30, light_y_center, 
                                                    50, light_y_center + 15, 
                                                    fill="red")
        self.canvas.tag_bind(self.left_triangle, "<Button-1>", self.send_decrease)

        # increase triangle right side
        self.right_triangle = self.canvas.create_polygon(350, light_y_center - 15, 
                                                     370, light_y_center, 
                                                     350, light_y_center + 15, 
                                                     fill="green")
        self.canvas.tag_bind(self.right_triangle, "<Button-1>", self.send_increase)

    def send_increase(self, event=None):
        self.strength = 0.0
        for i in self.light_status:
            #if light_status is True"
            if i:
                self.strength += 0.2
        #dont increase past 0
        if self.strength < 1:
            self.strength += 0.2
        self.strength = round(self.strength, 10)
        data = {listeningFor : self.strength}
        sendUDP(data)

    def send_decrease(self, event=None):
        self.strength = 0.0
        for i in self.light_status:
            #if light_status is True"
            if i:
                self.strength += 0.2
        #dont decrease past 0
        if self.strength > 0:
            self.strength -= 0.2
        self.strength = round(self.strength, 10)
        data = {listeningFor : self.strength}
        sendUDP(data)

    def update_lights(self, value):
        colors = ["red", "red", "yellow", "green", "green"]

        #reset all lights
        self.light_status = [False] * 5
        for i in range(min(value, 5) ,5):
            self.canvas.itemconfig(self.lights[i], fill="gray")

        # turn on lights based on received value from pump brain
        for i in range(min(value, 5)):  # out of bounds handling
            self.canvas.itemconfig(self.lights[i], fill=colors[i])
            self.light_status[i] = True

    def reset_lights(self):
        self.light_status = [False] * 5
        for light in self.lights:
            self.canvas.itemconfig(light, fill="gray")


SERVER_PORT = 8150
SERVER_IP = "127.0.0.1"
strength = 0.0
#initialize UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# start Tkinter GUI
root = tk.Tk()
app = LightControlApp(root,strength)

#start listening thread
listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

#start GUI
root.mainloop()

# close socket when program ends
server_socket.close()
