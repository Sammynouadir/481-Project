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
UDP_PORTS = [8161]

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
    **{key: 0 for key in PRESSURE_KEYS.keys()},           # For gauge animations
    **{key: 0 for key in INDICATOR_KEYS.keys()}             # For number indicators
}

prev_level_values = {key: 1 for key in LEVEL_KEYS.keys()} 


def udp_listener():
    """Listens for UDP messages"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 8161))
    sock.setblocking(False)


    while True:
        # Wait until at least one socket is ready for reading (with a timeout)
        readable, _, _ = select.select([sock], [], [], 0.5)
        for s in readable:
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                message = data.decode("utf-8")
                json_data = json.loads(message)

                #print("Received UDP message:")
                print(json.dumps(json_data, indent=4))

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
        return
    last_received_message = data


    print(json.dumps(data, indent=4))  #print incoming data

    new_values = prev_values.copy()
    new_levels = prev_level_values.copy()

    # Update pressure and flow values
    for key in PRESSURE_KEYS.keys():
        if key in data:
            new_values[key] = data[key]

    for key in INDICATOR_KEYS.keys():
        if key in data:
            new_values[key] = data[key]

    # Update level values (normalize from 0.0–1.0 to 0–100%)
    for key in LEVEL_KEYS.keys():
        if key in data:
            new_levels[key] = data[key]

    # Animate gauges
    for i, (key, ax) in enumerate(zip(PRESSURE_KEYS.keys(), gauge_axes)):
        pressure = data.get(key, prev_values.get(key, 125))
        old_val = prev_values.get(key, 125)
        if abs(pressure - old_val) > 0.5:
            animate_gauge(ax, old_val, pressure, PRESSURE_KEYS[key], fig_canvas, root)


        # Update flow indicators below gauges (including intake → total flow)
        if i == 0:
            flow_key = "total flow rate"
        else:
            flow_key = key.replace(" pressure", " flow rate")

        flow_value = data.get(flow_key, 0)
        indicator_label = indicator_labels[i]
        if indicator_label:
            flow_label = INDICATOR_KEYS.get(flow_key, "Flow")
            indicator_label.config(text=f"{flow_label}: {round(flow_value)}")


        prev_values[key] = pressure

    # Animate level indicators
    for i, level_key in enumerate(LEVEL_KEYS.keys()):
        old_level = prev_level_values[level_key]
        new_level = new_levels[level_key]
        #if abs(new_level - old_level) > 0.1:  # More sensitive change detection
        animate_level(level_canvases[i], old_level, new_level, level_colors[i])

    prev_values = new_values
    prev_level_values = new_levels



# Gauge Animation Functions
def ease_in_out(t):
    return t * t * (3 - 2 * t)

def animate_gauge(ax, start_value, end_value, label, fig_canvas, root, duration=400, steps=10):
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
        ax.text(x_outer * 1.2, y_outer * 1.2, str(i), ha='center', va='center', fontsize=8)

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
    width, height = 50, 150
    level_height = (value / 1) * height
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
fig, axes = plt.subplots(1, 5, figsize=(9, 2.2))

plt.tight_layout()
gauge_axes = axes

# Initialize gauges
for ax, label in zip(gauge_axes, PRESSURE_KEYS.values()):
    create_gauge(ax, 0, label)





# === Container to hold levels and gauges ===
main_container = Frame(root, bg="gray")
main_container.pack(pady=10)

# === Add level indicators to the left ===
level_container = Frame(main_container, bg="gray")
level_container.grid(row=0, column=0, rowspan=2, padx=20)

level_colors = ["blue", "red"]
level_canvases = []
for label, color in zip(LEVEL_KEYS.values(), ["blue", "red"]):
    frame = Frame(level_container, bg='gray')
    frame.pack(side='left', padx=10)  # <-- Change here
    Label(frame, text=label, bg='gray', font=("Arial", 12)).pack()
    level_canvas = Canvas(frame, width=50, height=150, bg="white")
    level_canvas.pack()
    update_level(level_canvas, 100, color)
    level_canvases.append(level_canvas)


# === Add gauges and flow indicators ===
gauge_container = Frame(main_container, bg="gray")
gauge_container.grid(row=0, column=1)

# Place the matplotlib figure canvas in the grid
fig_canvas = FigureCanvasTkAgg(fig, master=gauge_container)
fig_widget = fig_canvas.get_tk_widget()
fig_widget.grid(row=0, column=0, columnspan=5)

fig_canvas.draw()


# Flow indicator labels aligned under each gauge
indicator_labels = []

for i, key in enumerate(PRESSURE_KEYS.keys()):
    flow_key = key.replace(" pressure", " flow rate")

    if i == 0:
        # First label is for "total flow rate"
        flow_key = "total flow rate"
        flow_label = INDICATOR_KEYS.get(flow_key, "Total")
    else:
        flow_label = INDICATOR_KEYS.get(flow_key, "Flow")

    lbl = Label(gauge_container, text=f"{flow_label}: 0", font=("Arial", 12),
                bg="white", width=15, relief='solid', bd=1)
    lbl.grid(row=1, column=i, pady=(10, 0))
    indicator_labels.append(lbl)



root.mainloop()
