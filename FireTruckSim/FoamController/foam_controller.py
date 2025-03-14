import tkinter as tk
import json
import socket
import threading
import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)


class FoamController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Foam Controller")
        self.setup_network()
        
        self.power_state = False
        self.foam_concentration = 0.5
        self.last_message = {}
        
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
            
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def create_gui(self):
        frame = tk.Frame(self.root, bg='#FF4040', padx=20, pady=20)
        frame.pack(expand=True, fill='both')
        
        self.display = tk.Text(frame, height=6, width=25, bg='gray', 
                             font=('Courier', 12))
        self.display.pack(pady=10)
        
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
        
        self.update_display()
    
    def adjust_concentration(self, change):
        if self.power_state:
            self.foam_concentration = max(0.1, min(6.0, self.foam_concentration + change))
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
            data = {
                "foam system power": 1.0 if self.power_state else 0.0,
                "foam concentration": float(self.foam_concentration)
            }
            
            json_data = json.dumps(data).encode('utf-8')
            self.send_socket.sendto(json_data, ('127.0.0.1', 8150))
        except Exception as e:
            print(f"Send error: {e}")
    
    def start_listener(self):
        def listen():
            while True:
                try:
                    data = self.udp_socket.recvfrom(1024)[0]
                    message = json.loads(data.decode())
                    
                    if isinstance(message, list):
                        message_dict = {}
                        for item in message:
                            if isinstance(item, dict) and 'Key' in item and 'Value' in item:
                                message_dict[item['Key']] = item['Value']
                            elif len(item) == 2:  # Assume it's a key-value pair
                                key, value = item
                                message_dict[key] = value
                        self.last_message = message_dict
                    else:
                        self.last_message = message
                    
                    reset_value = self.last_message.get('Reset', 0)
                    if reset_value == 1:
                        self.power_state = False
                        self.foam_concentration = 0.5
                        self.root.after(0, self.toggle_power)
                    
                    self.root.after(0, self.send_update)
                    self.root.after(0, self.update_display)
                except Exception as e:
                    print(f"Network error: {str(e)}")
                    time.sleep(0.1)
        
        threading.Thread(target=listen, daemon=True).start()

if __name__ == "__main__":
    FoamController() 