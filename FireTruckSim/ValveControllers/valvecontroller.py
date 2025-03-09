import tkinter as tk
import socket
import json
import threading

def sendUDP(data):
    #encode data
    json_message = json.dumps(data)
    #send data
    server_socket.sendto(json_message.encode(), (SERVER_IP, int(SERVER_PORT)))

def listen():
    # Create a UDP socket to listen on
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_socket.bind((SERVER_IP, int(CURRENT_PORT)))  
    
    while True:
        # recieve meesage and adress from server with a file size of 1024 bytes
        message, address = listen_socket.recvfrom(1024)
        
        try:
            # decode json
            data = json.loads(message.decode())
            
            # check for reset
            if "Reset" in data and data["Reset"] == 1:
#                print("Reseting...")
                reset_valve_control()  # Call function to reset the valve control
                
        except Exception as e:            
            print("Error: ", e)

def reset_valve_control():
    app.reset_lights()

class LightControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Valve Control " + str(CURRENT_PORT))
        self.canvas = tk.Canvas(root, width=400, height=200, bg="light grey")
        self.canvas.pack()
        
        self.lights = []
        self.light_status = [False] * 5  # Track on/off state of lights
        self.create_lights()
        self.create_triangles()

    def create_lights(self):
        start_x = 100
        for i in range(5):
            x = start_x + i * 40
            light = self.canvas.create_oval(x, 50, x + 30, 80, fill="gray", outline="black")
            self.lights.append(light)
    
    def create_triangles(self):
        # Left triangle
        self.left_triangle = self.canvas.create_polygon(50, 100, 30, 120, 50, 140, fill="red")
        self.canvas.tag_bind(self.left_triangle, "<Button-1>", self.turn_off_lights)
        
        # Right triangle
        self.right_triangle = self.canvas.create_polygon(350, 100, 370, 120, 350, 140, fill="green")
        self.canvas.tag_bind(self.right_triangle, "<Button-1>", self.turn_on_lights)
    
    def turn_on_lights(self, event):
        #create and send udp update to brain
        data = {
            "valve controller increment" : 1
        }
        sendUDP(data)
        colors = ["red","red","yellow","green","green"]
        #loop until unlight light is found
        for i in range(5):
            if not self.light_status[i]:
                #turn on
                self.canvas.itemconfig(self.lights[i], fill=colors[i])
                self.light_status[i] = True
                break
    
    def turn_off_lights(self, event):
            #create and send udp update to brain
        data = {
            "valve controller decrement" : 1
        }
        sendUDP(data)
        #loop from back until lit light is found
        for i in range(4, -1, -1):
            if self.light_status[i]:
                #turn off
                self.canvas.itemconfig(self.lights[i], fill="gray")
                self.light_status[i] = False
                break

    def reset_lights(self):
        # Reset the light status
        self.light_status = [False] * 5
        for light in self.lights:
            self.canvas.itemconfig(light, fill="gray")

#select which port to listen on through valvesettings file
f = open("ValveSettings.txt", "r")
CURRENT_PORT = f.read()
CURRENT_IP = "127.0.0.1"
SERVER_PORT = 8150
SERVER_IP = "127.0.0.1"  # Change if running on a different machine

#initialize sending socket    
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

root = tk.Tk()
app = LightControlApp(root)

listener_thread = threading.Thread(target=listen)
listener_thread.daemon = True  #thread can exit when the program exits
listener_thread.start()

#run tkinter GUI
root.mainloop()

#end connections
server_socket.close()

