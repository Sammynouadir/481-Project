import pythonnet
pythonnet.load("coreclr")
import clr
import tkinter as tk  # Import tkinter
# from System.Collections.Generic import List, KeyValuePair
# import socket
# from tkinter import Tk, Label, Entry, Button, Text, Frame, messagebox, N, S, E, W
# from threading import Timer
clr.AddReference("PumpBrain")
from PumpBrain import PumpBrain


pumpBrain = PumpBrain()

# Create the main application window
root = tk.Tk()
root.title("Test Control Panel")
root.geometry("300x200")

# On Click
def on_button_click():
    print(pumpBrain.TestToolSupporter.TestStart())

# Buttons
button = tk.Button(root, text="click me", command=on_button_click)
button.pack()

# Start the event loop (keeps the window open)
root.mainloop()
