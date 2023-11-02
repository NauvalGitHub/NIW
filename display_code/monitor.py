"""
#title           :monitor.py
#description     :tkinter standard library setup to make python GUI template for NePower
#author          :Nauval Chantika
#date            :2023/09/22
#version         :1.0
#usage           :Energy Monitoring System, RS-485 and RS-232C interface
#notes           :
#python_version  :3.7.3
#==============================================================================
"""

# Import library
import tkinter as tk

class Monitor:
    def __init__(self, data):
        self.monitor = tk.Tk()
        self.monitor.title("NEPOWER Monitoring") # The title of pop up will appears
        self.monitor.geometry('1024x400+0+0') # widthxheight of the pop up in pixel size 1024x768
        #self.monitor.minsize('1024x400')
        #self.monitor.maxsize('1024x768')
        self.vars = [tk.StringVar() for _ in range(7)]

        # Get data for the first time
        self.update_data(data)

        # Create and pack labels to display the values
        labels = [tk.Label(self.monitor, textvariable=var, font=('Arial', 12), anchor='w') for var in self.vars]
        for label in labels:
            label.pack(pady=10, fill='x')  # padding for better visual separation

    def update_data(self, data):
        # The message that will shown in window with the layout
        self.vars[0].set(f"Converter Status:")
        self.vars[1].set(f"AC Voltage: {data[5]} V\t\tAC Current: {data[6]} A\t\tAC Power: {data[9]} kW")
        self.vars[2].set(f"DC Voltage: {data[4]} V\t\tProduced Power: {data[11]} kWh")
        self.vars[3].set(f"Baterry Status:")
        self.vars[4].set(f"Total Voltage: {data[1]} V\t\tAvg Temperature: {data[3]} C")
        self.vars[5].set(f"Inverter Status:")
        self.vars[6].set(f"Out Voltage: {data[14]} V\t\tOut Current: {data[13]}\t\tOut Power: {data[15]} kWh")
    
    def run(self):
        self.monitor.mainloop()

#--------------------------------------------------------------------------------------------------------------------------------------------------
# If this file is being run directly, then execute the following block

if __name__ == "__main__":
    # Dummy Data
    nodata = ["No data" for i in range(16)]
    #Initialize the Monitor class and run it
    my_monitor = Monitor(nodata)
    my_monitor.run()