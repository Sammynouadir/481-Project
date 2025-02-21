import tkinter as tk

# Function to handle starting the pump system
def start_system():
    system_status.set("Running")
    update_info("System started.")

# Function to handle stopping the pump system
def stop_system():
    system_status.set("Stopped")
    update_info("System stopped.")

# Function to handle pausing the pump system
def pause_system():
    system_status.set("Paused")
    update_info("System paused.")

# Function to handle connecting to fire hydrant
def connect_hydrant():
    update_info("Connected to Fire Hydrant.")

# Function to update the system info display
def update_info(message):
    info_display.config(state=tk.NORMAL)
    info_display.delete(1.0, tk.END)
    info_display.insert(tk.END, message)
    info_display.config(state=tk.DISABLED)

# Create main window
root = tk.Tk()
root.title("Firefighter Pump Panel Control")
root.geometry("500x400")  

# System status variable
system_status = tk.StringVar(value="Idle")

# Title Label
title_label = tk.Label(root, text="Firefighter Pump Panel Simulator", font=("Arial", 16))
title_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

# Current status label
status_label = tk.Label(root, text="Current Status:", font=("Arial", 12))
status_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

status_display = tk.Label(root, textvariable=system_status, font=("Arial", 12))
status_display.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Control Buttons
start_button = tk.Button(root, text="Start", width=15, command=start_system, bg="green")
start_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

stop_button = tk.Button(root, text="Stop", width=15, command=stop_system, bg="red")
stop_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

pause_button = tk.Button(root, text="Pause", width=15, command=pause_system, bg="yellow")
pause_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

connect_button = tk.Button(root, text="Connect to Fire Hydrant", width=20, command=connect_hydrant, bg="blue")
connect_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

# Information display area
info_label = tk.Label(root, text="System Info:", font=("Arial", 12))
info_label.grid(row=4, column=0, columnspan=3, padx=5, pady=10, sticky="w")

info_display = tk.Text(root, width=50, height=10, wrap=tk.WORD, font=("Arial", 10))
info_display.grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky="ew")
info_display.config(state=tk.DISABLED)

# Make all columns expand equally
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Start the Tkinter event loop
root.mainloop()


