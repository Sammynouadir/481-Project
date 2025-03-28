import tkinter as tk
from tkinter import Canvas, Label, Frame
import json
import socket
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import select

# UDP Configuration
UDP_PORTS = list(range(8160, 8167))  # Ports 8160-8166
BUFFER_SIZE = 1024  # Adjust as needed

# Flow and intake-related number indicators
INDICATOR_KEYS = {
    "total flow rate": "Total Flow",
    "discharge 1 flow rate": "D1 Flow",
    "discharge 2 flow rate": "D2 Flow",
    "discharge 3 flow rate": "D3 Flow",
}

# Tank levels
LEVEL_KEYS = {
    "normalized water tank level": "Water",
    "normalized foam tank level": "Foam",
}

# Pressure-specific gauges
PRESSURE_KEYS = {
    "intake pressure": "Intake",
    "master discharge pressure": "Discharge",
    "discharge 1 pressure": "D1 Pressure",
    "discharge 2 pressure": "D2 Pressure",
    "discharge 3 pressure": "D3 Pressure",
}

prev_values = {
    **{key: 125 for key in PRESSURE_KEYS.keys()},           # For gauge animations
    **{key: 0 for key in INDICATOR_KEYS.keys()}             # For number indicators
}

prev_level_values = {key: 50 for key in LEVEL_KEYS.keys()}  # Still valid


def udp_listener():
    """Listens for UDP messages using select() to reduce CPU usage."""
    udp_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in UDP_PORTS]

    for sock, port in zip(udp_sockets, UDP_PORTS):
        sock.bind(("0.0.0.0", port))
        sock.setblocking(False)

    while True:
        # Wait until at least one socket is ready for reading (with a timeout)
        readable, _, _ = select.select(udp_sockets, [], [], 0.5)
        for sock in readable:
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                message = data.decode("utf-8")
                json_data = json.loads(message)

                print(f"Received UDP message: {json_data}")
                root.after(0, lambda d=json_data: update_gauges_from_udp(d))

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

    new_values = prev_values.copy()
    new_levels = prev_level_values.copy()

    # Update only if the key is present in the new data
    for key in PRESSURE_KEYS.keys():
        if key in data:
            new_values[key] = data[key]
    
    for key in INDICATOR_KEYS.keys():
        if key in data:
            new_values[key] = data[key]
    
    for key in LEVEL_KEYS.keys():
        if key in data:
            new_levels[key] = data[key] * 100  # Normalize
    # Update gauge displays
    for i, (key, ax) in enumerate(zip(PRESSURE_KEYS.keys(), gauge_axes)):
        pressure = data.get(key, prev_values.get(key, 125))
        animate_gauge(ax, prev_values.get(key, 125), pressure, PRESSURE_KEYS[key], fig_canvas, root)

        # Update corresponding flow indicator below (skip intake)
        if i > 0:
            flow_key = key.replace(" pressure", " flow rate")
            flow_value = data.get(flow_key, 0)
            indicator_label = indicator_labels[i]
            if indicator_label:
                indicator_label.config(text=f"{INDICATOR_KEYS.get(flow_key, 'Flow')}: {round(flow_value)}")

        prev_values[key] = pressure



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

def create_gauge(ax, value, label, min_val=0, max_val=500):
    START_ANGLE, END_ANGLE = 210, -25
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'k', lw=3)

    for i in range(min_val, max_val + 1, 50):
        angle = np.radians(START_ANGLE - (i - min_val) * ((START_ANGLE - END_ANGLE) / (max_val - min_val)))
        x_outer, y_outer = np.cos(angle), np.sin(angle)
        x_inner, y_inner = 0.8 * np.cos(angle), 0.8 * np.sin(angle)
        ax.plot([x_outer, x_inner], [y_outer, y_inner], 'k', lw=2)
        ax.text(x_outer * 1.2, y_outer * 1.2, str(i), ha='center', va='center', fontsize=10)

    # Draw needle as a line and keep reference
    angle = np.radians(START_ANGLE - ((value - min_val) / (max_val - min_val)) * (START_ANGLE - END_ANGLE))
    needle_line, = ax.plot([0, 0.8 * np.cos(angle)], [0, 0.8 * np.sin(angle)], 'r', lw=3)
    ax.needle = needle_line



    ax.set_title(label, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

def update_gauge(ax, value, label, START_ANGLE=210, END_ANGLE=-25, min_val=0, max_val=500):
    angle = np.radians(START_ANGLE - ((value - min_val) / (max_val - min_val)) * (START_ANGLE - END_ANGLE))
    x, y = 0.8 * np.cos(angle), 0.8 * np.sin(angle)

    if hasattr(ax, 'needle'):
        ax.needle.set_data([0, x], [0, y])




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
for ax, label in zip(gauge_axes, PRESSURE_KEYS.values()):
    create_gauge(ax, 125, label)





# === Create a container to grid-align gauges and indicators ===
gauge_container = Frame(root, bg="gray")
gauge_container.pack(pady=10)

# Place the existing matplotlib figure canvas in the grid
fig_canvas = FigureCanvasTkAgg(fig, master=gauge_container)
fig_widget = fig_canvas.get_tk_widget()
fig_widget.grid(row=0, column=0, columnspan=5)

fig_canvas.draw()

# Flow indicator labels aligned under each gauge
indicator_labels = []

for i, key in enumerate(PRESSURE_KEYS.keys()):
    if i == 0:
        indicator_labels.append(None)
        continue

    flow_key = key.replace(" pressure", " flow rate")
    flow_label = INDICATOR_KEYS.get(flow_key, "Total")

    lbl = Label(gauge_container, text=f"{flow_label}: 0", font=("Arial", 12),
                bg="white", width=15, relief='solid', bd=1)
    lbl.grid(row=1, column=i, pady=(10, 0))
    indicator_labels.append(lbl)


level_canvases = []
for label, color in zip(LEVEL_KEYS.values(), ["blue", "red"]):
    frame = Frame(root, bg='gray')
    frame.pack(side=tk.LEFT, padx=20)
    Label(frame, text=label, bg='gray', font=("Arial", 12)).pack()
    level_canvas = Canvas(frame, width=50, height=200, bg="white")
    level_canvas.pack()
    update_level(level_canvas, 50, color)
    level_canvases.append(level_canvas)

root.mainloop()
