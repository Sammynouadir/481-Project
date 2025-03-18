import tkinter as tk
from tkinter import Canvas, Label, Frame
import json
import socket
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# UDP Configuration
UDP_PORTS = list(range(8160, 8167)) 
BUFFER_SIZE = 1024  

# Gauge keys
GAUGE_KEYS = {
    "intake pressure": "Intake",
    "master discharge pressure": "Discharge",
    "discharge 1 pressure": "D1",
    "discharge 2 pressure": "D2",
    "discharge 3 pressure": "D3",
}

LEVEL_KEYS = {
    "normalized water tank level": "Water",
    "normalized foam tank level": "Foam",
}

prev_values = {key: 125 for key in GAUGE_KEYS.keys()}
prev_level_values = {key: 50 for key in LEVEL_KEYS.keys()}

# UDP Listener
def udp_listener():
    #Listens for UDP messages
    udp_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in UDP_PORTS]

    for sock, port in zip(udp_sockets, UDP_PORTS):
        sock.bind(("0.0.0.0", port))
        sock.settimeout(1.0)  # Prevent blocking
        sock.setblocking(False)  # Non-blocking mode (Windows replacement for MSG_DONTWAIT)

    while True:
        for sock in udp_sockets:
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)  # Non-blocking receive
                message = data.decode("utf-8")
                json_data = json.loads(message)  # Parse JSON

                print(f"Received UDP message: {json_data}")

                # Schedule UI update in the main Tkinter thread
                root.after(0, lambda: update_gauges_from_udp(json_data))

            except socket.timeout:
                continue  # Avoid blocking other sockets
            except BlockingIOError:
                continue  # No data available, move to next socket
            except Exception as e:
                print(f"Error receiving UDP message: {e}")

# Start UDP listener in a separate thread
udp_thread = threading.Thread(target=udp_listener, daemon=True)
udp_thread.start()

last_received_message = None  # Store the last received message

def update_gauges_from_udp(data):
    global prev_values, prev_level_values, last_received_message

    # Ignore duplicate messages
    if data == last_received_message:
        return  # Skip processing if it's the same as last time

    last_received_message = data  # Store latest message

    new_values = {key: data.get(key, prev_values[key]) for key in GAUGE_KEYS.keys()}
    new_levels = {key: data.get(key, prev_level_values[key]) * 100 for key in LEVEL_KEYS.keys()}  # Normalize %

    # Update gauge displays
    for key, ax in zip(GAUGE_KEYS.keys(), gauge_axes):
        animate_gauge(ax, prev_values[key], new_values[key], GAUGE_KEYS[key], fig_canvas, root)

    # Update level indicators
    for key, (level_canvas, color) in zip(LEVEL_KEYS.keys(), zip(level_canvases, ["blue", "red"])):
        animate_level(level_canvas, prev_level_values[key], new_levels[key], color)

    prev_values = new_values
    prev_level_values = new_levels


# Gauge Animation Functions
def ease_in_out(t):
    return t * t * (3 - 2 * t)

def animate_gauge(ax, start_value, end_value, label, fig_canvas, root, duration=1000, steps=20):
    step_values = [start_value + (end_value - start_value) * ease_in_out(i / steps) for i in range(steps + 1)]
    
    def step(i=0):
        if i > steps:
            return
        update_gauge(ax, step_values[i], label)
        fig_canvas.draw_idle()
        root.after(duration // steps, step, i + 1)

    step()

def create_gauge(ax, value, label, min_val=0, max_val=250):
    START_ANGLE, END_ANGLE = 210, -25
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'k', lw=3)

    for i in range(min_val, max_val+1, 50):
        angle = np.radians(START_ANGLE - (i - min_val) * ((START_ANGLE - END_ANGLE) / (max_val - min_val)))
        x_outer, y_outer = np.cos(angle), np.sin(angle)
        x_inner, y_inner = 0.8 * np.cos(angle), 0.8 * np.sin(angle)
        ax.plot([x_outer, x_inner], [y_outer, y_inner], 'k', lw=2)
        ax.text(x_outer * 1.2, y_outer * 1.2, str(i), ha='center', va='center', fontsize=10)

    ax.needle = None
    update_gauge(ax, value, label, START_ANGLE, END_ANGLE)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

def update_gauge(ax, value, label, START_ANGLE=210, END_ANGLE=-25, min_val=0, max_val=250):
    if hasattr(ax, 'needle') and ax.needle:
        ax.needle.remove()
    angle_range = START_ANGLE - END_ANGLE
    angle = np.radians(START_ANGLE - ((value - min_val) / (max_val - min_val)) * angle_range)
    ax.needle = ax.arrow(0, 0, 0.8 * np.cos(angle), 0.8 * np.sin(angle), 
                          head_width=0.1, head_length=0.1, fc='r', ec='r')

    while ax.texts:
        ax.texts[-1].remove()

    ax.text(0, -1.3, str(round(value)), fontsize=12, ha='center', bbox=dict(facecolor='white', edgecolor='black'))
    ax.set_title(label, fontsize=10)

def update_level(level_canvas, value, color):
    level_canvas.delete("all")
    width, height = 50, 200
    level_height = (value / 100) * height
    level_canvas.create_rectangle(10, height - level_height, 40, height, fill=color)
    level_canvas.create_rectangle(10, 0, 40, height, outline="black", width=2)
    level_canvas.create_text(25, height + 10, text=f"{value}%", font=("Arial", 12))

def animate_level(level_canvas, start_value, end_value, color, duration=1000, steps=20):
    step_values = [start_value + (end_value - start_value) * ease_in_out(i / steps) for i in range(steps + 1)]
    
    def step(i=0):
        if i > steps:
            return
        update_level(level_canvas, step_values[i], color)
        root.after(duration // steps, step, i + 1)

    step()

# Initialize Tkinter
root = tk.Tk()
root.title("Pump Panel Dashboard")
root.configure(bg='gray')

# Create Matplotlib figure
fig, axes = plt.subplots(1, 5, figsize=(12, 3))
plt.tight_layout()
gauge_axes = axes

# Initialize gauges
for ax, label in zip(gauge_axes, GAUGE_KEYS.values()):
    create_gauge(ax, 125, label)

fig_canvas = FigureCanvasTkAgg(fig, master=root)
fig_canvas.get_tk_widget().pack()
fig_canvas.draw()

level_canvases = []
for label, color in zip(LEVEL_KEYS.values(), ["blue", "red"]):
    frame = Frame(root, bg='gray')
    frame.pack(side=tk.LEFT, padx=20)
    Label(frame, text=label, bg='gray', font=("Arial", 12)).pack()
    level_canvas = Canvas(frame, width=50, height=200, bg="white")
    level_canvas.pack()
    update_level(level_canvas, 50, color)
    level_canvases.append(level_canvas)

# Start UDP listener
threading.Thread(target=udp_listener, daemon=True).start()

root.mainloop()
