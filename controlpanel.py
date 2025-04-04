import pythonnet
pythonnet.load("coreclr")
import clr
from System.Collections.Generic import List
import socket
from tkinter import Tk, Label, Text, Frame, Button, N, S, E, W

# Add reference to the C# .dll
clr.AddReference("PumpBrain")

# Import the namespace
from PumpBrain import PumpBrain

class UdpMessageApp:
    def __init__(self, root):
        # Create an object of the C# PumpBrain class
        self.pump_brain = PumpBrain()
        
        # Check if CPInterface exists and use it
        if hasattr(self.pump_brain, 'CPInterface'):
            self.cp_interface = self.pump_brain.CPInterface
            print("CPInterface exists!")
        else:
            self.cp_interface = self.pump_brain
            print("CPInterface does not exist!")

        # Debug: Print the initial hydrant state
        print("Initial Hydrant Connected State:", self.cp_interface.GetHydrantConnected())
        
        # Force initial hydrant state to Disconnected
        self.cp_interface.SetHydrantConnected(False)
        print("Forced Hydrant Connected State to:", self.cp_interface.GetHydrantConnected())

        # Ensure Pump is Running
        self.cp_interface.SetPauseState(False)  
        
        # Initialize the root window
        self.root = root
        self.root.title("Pump Control Panel")
        
        # Configure grid resizing weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        #making the window long to allow space for other components
        self.root.geometry("400x700")  

        # --- Pump State Section ---
        state_frame = Frame(root, borderwidth=2, relief="groove")
        state_frame.grid(row=0, column=0, padx=10, pady=10, sticky=N+S+E+W)
        
        Label(state_frame, text="Pump State", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.pump_state_label = Label(state_frame, text="State: Unknown")
        self.pump_state_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # --- Discharge Information Section ---
        discharge_frame = Frame(root, borderwidth=2, relief="groove")
        discharge_frame.grid(row=0, column=1, padx=10, pady=10, sticky=N+S+E+W)
        
        Label(discharge_frame, text="Discharge Information", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.discharge_text = Text(discharge_frame, wrap="word", height=30, width=30)
        self.discharge_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=N+S+E+W)
        
        # --- Hydrant Information Section ---
        hydrant_frame = Frame(root, borderwidth=2, relief="groove")
        hydrant_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=N+S+E+W)
        
        Label(hydrant_frame, text="Hydrant Information", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.hydrant_connected_label = Label(hydrant_frame, text="Connected: Unknown")
        self.hydrant_connected_label.grid(row=1, column=0, padx=10, pady=5, sticky=W)
        self.hydrant_pressure_label = Label(hydrant_frame, text="Pressure: Unknown")
        self.hydrant_pressure_label.grid(row=2, column=0, padx=10, pady=5, sticky=W)
        self.hydrant_flowrate_label = Label(hydrant_frame, text="Flowrate: Unknown")
        self.hydrant_flowrate_label.grid(row=3, column=0, padx=10, pady=5, sticky=W)
        
        def toggle_hydrant():
            # Check current state and toggle it
            if self.cp_interface.GetHydrantConnected():
                print("Disconnecting hydrant")
                self.cp_interface.SetHydrantConnected(False)
                print("Hydrant State: ", self.cp_interface.GetHydrantConnected())
            else:
                print("Connecting hydrant")
                self.cp_interface.SetHydrantConnected(True)
                print("Hydrant State: ", self.cp_interface.GetHydrantConnected())
                #update ui with a delay
            self.root.after(500, self.update_ui)  

        toggle_button = Button(hydrant_frame, text="Toggle Fire Hydrant", command=toggle_hydrant)
        toggle_button.grid(row=4, column=0, padx=10, pady=5, sticky=W)
        
        # --- Start/Stop Button ---
        self.running = True
        def toggle_updates():
            self.running = not self.running
            if self.running:
                self.cp_interface.SetPauseState(False)
                self.update_ui()
                start_stop_button.config(text="Stop")
            else:
                self.cp_interface.SetPauseState(True)
                start_stop_button.config(text="Start")
        
        start_stop_button = Button(root, text="Stop", command=toggle_updates)
        start_stop_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Start periodic updates
        self.update_ui()

    def update_ui(self):
        if not self.running:
            return
        
        try:
            # Checking if Pump is Running
            self.cp_interface.SetPauseState(False)

            # Update pump state
            pump_state = "Running" if not self.cp_interface.GetPauseState() else "Paused"
            self.pump_state_label.config(text=f"State: {pump_state}")

            # Update hydrant information
            hydrant_connected = "Connected" if self.cp_interface.GetHydrantConnected() else "Disconnected"
            hydrant_pressure = self.cp_interface.GetHydrantPressure()
            hydrant_flowrate = self.cp_interface.GetHydrantFlowRate()
            
            self.hydrant_connected_label.config(text=f"Connected: {hydrant_connected}")
            self.hydrant_pressure_label.config(text=f"Pressure: {hydrant_pressure:.2f} psi")
            self.hydrant_flowrate_label.config(text=f"Flowrate: {hydrant_flowrate:.2f} gpm")

            # Update discharge information
            descriptions = self.cp_interface.GetDischargeDescriptions()
            pressures = self.cp_interface.GetNozzlePressures()
            flowrates = self.cp_interface.GetNozzleFlowRates()
            
            discharge_info = ""
            for i, (desc, pressure, flowrate) in enumerate(zip(descriptions, pressures, flowrates)):
                discharge_info += f"Discharge {i+1}:\n"
                discharge_info += f"  Description: {desc}\n"
                discharge_info += f"  Pressure: {pressure:.2f} psi\n"
                discharge_info += f"  Flowrate: {flowrate:.2f} gpm\n\n"

            self.discharge_text.delete("1.0", "end")
            self.discharge_text.insert("1.0", discharge_info)

        except Exception as e:
            print(f"Error updating UI: {e}")

        self.root.after(1000, self.update_ui)


    def on_close(self):
        self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = Tk()
    app = UdpMessageApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()



 


