"""
#title           :frame_es.py
#description     : Create Class for Energy Storage Frame for NePower Monitoring
#author          :Nauval Chantika
#date            :2023/09/25
#version         :1.0
#usage           :Energy Monitoring System, RS-485 and RS-232C interface
#notes           :
#python_version  :3.11.5
#==============================================================================
"""
import os
import socket
import time
import threading
import tkinter as tk
from tkinter import ttk, font

# Constants
THEME_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
THEME_PATH = os.path.join(THEME_DIR_PATH, 'theme', 'Azure-ttk-theme', 'azure.tcl')
SOCKET_PATH = '/tmp/ipc_socket'
INTERVAL = 15  # in seconds
DEFAULT_ES_DATA = ["none" for _ in range(19)]
ES_TYPE = 'Default'

class StorageFrame(ttk.Frame):
    def __init__(self, master, ES_data, ES_type): # If there are other arguments: (self, master, arg5, arg6)
        super().__init__(master)
        # All setup nad initial command
        self.clss = master

        #______________________________________________

        # Register all arguments another master in here
        #self.arg5 = arg5
        #self.arg6 = arg6
        self.ES_data = ES_data
        #______________________________________________

        # Register all variable you need to make widgets here
        self.time_vars = tk.StringVar()
        self.com_vars = []
        self.label_texts = []

        #______________________________________________

        # Register/Call all functions that is needed to run automatically
        self.ES_configuration()
        self.ES_type = ES_type
        self.create_widgets(ES_data)

        #______________________________________________

        for i in range(5):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(1, weight=1)

    # List of Function start from here
    def create_widgets(self, ES_data):
        # Make widgets here
        time_label = tk.Label(self, textvariable=self.time_vars, font=('Helvetica', 10), anchor='w')
        Img_labels = tk.Label(self, text="BMS Schematics Right Here", font=font.Font(family='Helvetica', size=10, weight= 'bold'), bg= "#d90429")

        time_label.grid(row=0, column=0, sticky='news')
        Img_labels.grid(row=1, column=2, pady=10, sticky='news')

        # Load the image use " Tkinter's 'PhotoImage' " or " Pillow Package "
        # Using PIL -----------If you want to use .jpg, Make sure install 'Pillow' package first: pip install Pillow
        #image_path = Image.open(file='path/to/file.jpg') # using PIL
        #BMS_schematics = ImageTk.PhotoImage(image_path)
        # Tkinter ------------ only work for .png and .gif
        #image_path = 'path/to/file.png'
        #BMS_schematics = tk.PhotoImage(file=image_path)
        #schematic_label = tk.Label(self, image=BMS_schematics)

        default_font_fg = self.master.option_get('foreground', 'black')

        for component, details in self.configuration[f'{self.ES_type}']['components'].items():
            vars_number = details['vars']
            labels_number = details['labels']
            vars = [tk.StringVar() for _ in range(vars_number)]
            labels = [
                tk.Label(self, 
                         textvariable=vars[i], 
                         font=('Helvetica', 15, 'bold' if i == 0 else 'normal'), 
                         fg= default_font_fg if i == 0 or (i % 2) == 1  else '#d90429',
                         justify= 'left' if i == 0 else 'center')
            for i in range(len(vars))
            ]
            row_header, column_header = labels_number[0]+1, labels_number[1]
            row_value, column_value = labels_number[0]+2, labels_number[1]
            for j, label in enumerate(labels):
                if j == 0:
                    label.grid(row=labels_number[0], column=labels_number[1], pady=10, sticky='ew')
                elif (j % 2) == 1:
                    label.grid(row=row_header, column=column_header, pady=10, sticky='ew')
                    column_header += 1
                else: #(i % 2 == 0)
                    label.grid(row=row_value, column=column_value, pady=10, sticky='ew')
                    column_value += 1
                if column_header == 5:
                    row_header += 2
                    column_header = 0
                if column_value == 5:
                    row_value += 2
                    column_value = 0
            self.com_vars.append(vars)

        # Update the text of the labels with the provided ES_data
        self.update_ES_data(ES_data)

    def update_ES_data(self, ES_data): # Update labels with ES_data
        # Layouting
        time_label_text = f"{ES_data[0]}"
        
        for i, (component, details) in enumerate(self.configuration[f'{self.ES_type}']['components'].items()):
            parameters = details['parameters']
        
            # Directly set the main component name to com_vars
            if len(self.com_vars[i]) > 0:
                self.com_vars[i][0].set(f"{component} Parameter")
        
            # Set the parameter names and values
            for idx, (name, value) in enumerate(parameters):
                if (2*idx + 1) < len(self.com_vars[i]):
                    self.com_vars[i][2*idx + 1].set(name)
                    self.com_vars[i][2*idx + 2].set(f"{ES_data[value]}")
                else:
                    print(f"Warning: com_vars[{i}] does not have a position for indices {2*idx + 1} and {2*idx + 2}.")

        # Store the update Layout
        self.time_vars.set(time_label_text)

        #for component, details in self.configuration[f'{self.ES_type}']['components'].items():
        #    parameters = details['parameters']
        #    label_text = [f"{component} Parameter"]
        #    for (name, value) in parameters:
        #        label_text.append(name)
        #        label_text.append(value)
        #    self.label_texts.append(label_text)

        # Store the update Layout
        #self.time_vars.set(time_label_text)

        #for i, label_text in enumerate(self.label_texts):
        #    for j, text in enumerate(label_text):
        #        self.com_vars[i][j].set(text)

    def ES_configuration(self):
        self.configuration = {
            'Default': {
                'schematic': 'path/to/file/BMS_Default.png',
                'components': {
                    'Converter': {
                        'vars': 9,
                        'labels': [2, 0],
                        'parameters': [
                            (f"AC Voltage (V)", 7),
                            (f"AC Current (A)", 8),
                            (f"AC Power (kW)", 12),
                            (f"DC Voltage (V)", 6)
                        ]
                    },
                    'Battery': {
                        'vars': 5,
                        'labels': [5, 0],
                        'parameters': [
                            (f"Total Voltage (V)", 4),
                            (f"Temperature (C)", 2)
                        ]
                    },
                    'Inverter': {
                        'vars': 9,
                        'labels': [8, 0],
                        'parameters': [
                            (f"AC Voltage (V)", 17),
                            (f"AC Current (A)", 16),
                            (f"Output Power (kW)", 18),
                            (f"AC Freq (Hz)", 15)
                        ]
                    }
                }
            }
        }

def setup_socket():
    #_____Only for UNIX OS_______________________________________________
    # Make sure to remove the socket if it exists from prior runs
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
        print("Socket path exists. Removing...")
    
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:   
        server_socket.bind(SOCKET_PATH)
    except socket.error as e:
        print(f"Error: Unable to bind socket. Address may be incorrect. {e}")
        exit(1)  # Exit with an error code

    print(f"Socket bound to {SOCKET_PATH}")
    server_socket.listen(30)
    print("Server listening for incoming connections...")
    
    
    #____________________________________________________________________
    #_____Can be compatible for windows__________________________________
    #socket_address = ('localhost', 9000) # Change the ('hostname', port) to the your target
    #server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #try:
    #    server_socket.bind(socket_address)
    #except socket.error as e:
    #    print(f"Error: Unable to bind socket. Address may be incorrect. {e}")
    #    exit(1)  # Exit with an error code

    #print(f"Socket bound to {SOCKET_PATH}")
    #server_socket.listen(30)
    #print("Server listening for incoming connections...")
    #____________________________________________________________________
    connection, _ = server_socket.accept()
    return connection, server_socket

def update_frame(content_instance, root_instance, conn, server_sock):
    try:
        # Get data from other script
        data = conn.recv(1024).decode('utf-8').split(',')
        print("Received data:", data)
        if len(data) != len(DEFAULT_ES_DATA):  # Check the data length
            print(f"Warning: Received data of length {len(data)} but expected length {len(DEFAULT_ES_DATA)}")
            show = DEFAULT_ES_DATA.copy()
        else:
            show = data
            conn.sendall(b'ACK') # Send an acknowledgment back to the client
    except (ConnectionResetError, socket.timeout):
        # This error is raised if the client disconnects abruptly.
        print("Connection reset or timed out. Re-establishing connection...")
        conn, _ = server_sock.accept()
        show = ["OUT" for _ in range(19)]
    except Exception as e:
        # General catch-all for other exceptions
        print(f"An error occurred: {e}. Waiting for a new connection...")
        conn, _ = server_sock.accept()
        show = ["Error" for _ in range(19)]
    
    #Schedule the next update after XX miliseconds
    content_instance.update_ES_data(show)
    root_instance.after(INTERVAL * 1000, lambda: update_frame(content_instance, root_instance, conn, server_sock))


if __name__ == "__main__":
    conn, server_sock = setup_socket()
    server_sock.settimeout(INTERVAL) # Set a timeout in seconds for accepting connections.
    
    #Initialize the window tkinter
    root = tk.Tk()
    root.title("NePower Monitoring")
    root.geometry("1020x600")
    root.tk.call('source', THEME_PATH)
    root.tk.call('set_theme','dark')
    #________________________________________________________________________

    # Input data conditioning for each frame
    
    #________________________________________________________________________

    # Run
    # if there any arguments other than master include it: main_window = MainContent(master, arg1, arg2, ..., arg-n)
    content = StorageFrame(root, DEFAULT_ES_DATA, ES_TYPE)
    content.grid(row=0, column=0, sticky='nsew')
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=0)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    update_frame(content, root, conn, server_sock)
    
    root.mainloop()
    #________________________________________________________________________