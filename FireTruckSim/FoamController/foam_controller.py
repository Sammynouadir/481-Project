import pythonnet
pythonnet.load("coreclr")
import clr
from System.Collections.Generic import List, KeyValuePair
import tkinter as tk
import json
import socket
import threading
import time
import sys
import os

# Setup paths and load PumpBrain
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

try:
    clr.AddReference("PumpBrain")
    from PumpBrain import PumpBrain
except Exception as e:
    print(f"Error loading PumpBrain.dll: {e}")

class FoamController:
    def __init__(self):
        # Initialize window and network
        self.root = tk.Tk()
        self.root.title("Foam Controller")
        self.setup_network()
        
        # State variables
        self.power_state = False
        self.foam_concentration = 0.5
        self.last_message = {}
        self.pump_brain = PumpBrain()
        
        self.create_gui()
        self.start_listener()
        self.root.mainloop()
    
    def setup_network(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.udp_socket.bind(('127.0.0.1', 8152))
        except:
            print("Port 8152 in use. Close other instances.")
            self.root.destroy()
    
    def create_gui(self):
        # Main frame - using a medium red color
        frame = tk.Frame(self.root, bg='#FF4040', padx=20, pady=20)
        frame.pack(expand=True, fill='both')
        
        # Display
        self.display = tk.Text(frame, height=6, width=25, bg='#90EE90', 
                             font=('Courier', 12))
        self.display.pack(pady=10)
        
        # Buttons - using same red for background
        btn_frame = tk.Frame(frame, bg='#FF4040')
        btn_frame.pack(pady=10)
        
        self.power_btn = tk.Button(btn_frame, text="POWER", bg="red",
                                  command=self.toggle_power,
                                  width=8, height=2)
        self.power_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.up_btn = tk.Button(btn_frame, text="↑", bg="green",
                               command=lambda: self.adjust_concentration(0.1),
                               state='disabled',
                               width=8, height=2)
        self.up_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.down_btn = tk.Button(btn_frame, text="↓", bg="green",
                                 command=lambda: self.adjust_concentration(-0.1),
                                 state='disabled',
                                 width=8, height=2)
        self.down_btn.grid(row=1, column=1, padx=5, pady=5)
        
        self.update_display()
    
    def toggle_power(self):
        self.power_state = not self.power_state
        state = 'normal' if self.power_state else 'disabled'
        color = 'green' if self.power_state else 'red'
        
        self.power_btn.config(bg=color)
        self.up_btn.config(state=state)
        self.down_btn.config(state=state)
        self.display.config(bg='#90EE90' if self.power_state else 'gray')
        
        self.send_update()
        self.update_display()
    
    def adjust_concentration(self, change):
        if self.power_state:
            self.foam_concentration = max(0.1, min(6.0, self.foam_concentration + change))
            self.send_update()
            self.update_display()
    
    def update_display(self):
        self.display.delete(1.0, tk.END)
        self.display.insert(1.0, 
            f"TANK 1 CLASS A\n\n"
            f"Foam Flow    {self.last_message.get('foam flow rate', 0.0):.1f} GPM\n"
            f"Water Flow   {self.last_message.get('total flow rate', 0.0):.1f} GPM\n"
            f"Foam Percent {self.foam_concentration:.1f}%\n"
            f"Foam Used    {self.last_message.get('foam flow total', 0.0):.1f} Gal\n"
            f"Water Used   {self.last_message.get('water used', 0.0):.1f} Gal")
    
    def send_update(self):
        try:
            data = List[KeyValuePair[str, float]]()
            data.Add(KeyValuePair[str, float]("foam system power", 
                                             1.0 if self.power_state else 0.0))
            data.Add(KeyValuePair[str, float]("foam concentration", 
                                             float(self.foam_concentration)))
            self.pump_brain.TestToolSupporter.BackDoorSendTestUDP(data, 8150)
        except Exception as e:
            print(f"Send error: {e}")
    
    def start_listener(self):
        def listen():
            while True:
                try:
                    data = self.udp_socket.recvfrom(1024)[0]
                    message = json.loads(data.decode())
                    self.last_message = message
                    
                    if message.get("Reset") == 1:
                        self.power_state = False
                        self.foam_concentration = 0.5
                        self.root.after(0, self.toggle_power)
                    
                    self.root.after(0, self.update_display)
                    self.root.after(0, self.send_update)
                except Exception as e:
                    print(f"Network error: {e}")
                    time.sleep(0.1)
        
        threading.Thread(target=listen, daemon=True).start()

if __name__ == "__main__":
    FoamController() 