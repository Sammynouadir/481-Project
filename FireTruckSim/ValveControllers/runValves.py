import subprocess
import time

#what ports will be listening on and how many instances will open
ports = [8161, 8162, 8163, 8164, 8165, 8166]

for port in ports:
        with open("ValveSettings.txt", "w") as file:  # reset file each time
            file.write(str(port))  #write port number down for valvecontroller.py to use for setup
        
        process1 = subprocess.Popen(["python", "valvecontroller.py"])

        #read and write functions take too long so the program has to wait before opening more threads
        #to ensure the proper port is selected
        time.sleep(0.1)



 
