"""
#title           :main__modbus.py
#description     :modbus Communication between Modbus devices and Raspberry Pi + RS485/CAN Hat + USB-to-RS232C Adaptor
#author          :Nicholas Putra Rihandoko, Nauval Chantika
#date            :2023/09/22
#version         :1.0
#usage           :Energy Monitoring System, RS-485 and RS-232C interface
#notes           :
#python_version  :3.9.2
#==============================================================================
"""

# Import library
import datetime # RTC Real Time Clock
import time
import os
import socket
import threading
import logging
from pymodbus.client import ModbusSerialClient as ModbusClient
import query
from lib import kyuden_battery_72kWh as battery
from lib import yaskawa_D1000 as converter
from lib import yaskawa_GA500 as inverter
#from lib import tristar_MPPT as charger

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define Modbus communication parameters
port            = '/dev/ttyS0'    # for RS485/CAN Hat
port_id0        = 'Prolific_Technology_Inc' # for USB-to-RS232C adaptor
port0           = os.popen('sudo bash {}/get_usb.bash {}'.format(os.path.dirname(os.path.abspath(__file__)), port_id0)).read().strip()
method          = 'rtu'
bytesize        = 8
stopbits        = 1
parity          = 'N'
baudrate        = 9600   # data/byte transmission speed (in bytes per second)
client_latency  = 100   # the delay time master/client takes from receiving response to sending a new command/request (in milliseconds)
timeout         = 1   # the maximum time the master/client will wait for response from slave/server (in seconds)
interval        = 30   # the period between each subsequent communication routine/loop (in seconds)

# Define MySQL Database parameters
mysql_server    = {"host":"machinedatanglobal.c4sty2dpq6yv.ap-northeast-1.rds.amazonaws.com",
                    "user":"Nglobal_root_NIW",
                    "password":"Niw_Machinedata_11089694",
                    "db":"NEPOWER_1",
                    "table":"dataparameter",
                    "port":3306}
#mysql_server    = {"host":"10.4.171.204",
#                    "user":"root",
#                    "password":"niw2082023",
#                    "db":"test",
#                    "table":"not_used",
#                    "port":3306}
mysql_timeout   = 3 # the maximum time this device will wait for completing MySQl query (in seconds)
mysql_interval  = 60 # the period between each subsequent update to database (in seconds)

# Another Constants
SYNC_WAIT_TIME = 5  # Time (in seconds) to wait before actual data transfer.

#query.debugging()  # Monitor Modbus communication for debugging

def setup_modbus():
    global port, port0, method, bytesize, stopbits, parity, baudrate, client_latency, timeout
    # Set each Modbus communication port specification
    client = ModbusClient(port=port, method=method, stopbits=stopbits, bytesize=bytesize, parity=parity, baudrate=baudrate, timeout=timeout)
    client0 = ModbusClient(port=port0, method=method, stopbits=stopbits, bytesize=bytesize, parity=parity, baudrate=baudrate, timeout=timeout)
    # Connect to the Modbus serial
    client.connect()
    client0.connect()
    # Define the Modbus slave/server (nodes) objects
    bat = battery.node(slave=1, name='BATTERY', client=client0, delay=client_latency, max_count=20, increment=1, shift=0)
    conv = converter.node(slave=2, name='CONVERTER', client=client, delay=client_latency, max_count=20, increment=1, shift=0)
    inv = inverter.node(slave=3, name='INVERTER', client=client, delay=client_latency, max_count=20, increment=1, shift=0)
    #chr = charger.node(slave=4, name='SOLAR CHARGER', client=client, delay=client_latency)
    server = [conv, bat, inv]
    return server

def read_modbus(server):
    addr=[["DC_Voltage_Command","AC_Voltage","AC_Current","DC_Power","AC_Frequency","Power_Factor","AC_Power","Consumed_Power_kWh","Produced_Power_kWh"],
          ["SOC","Total_Voltage","Cell_Voltage_avg","Temperature_avg"],
          ["Output_Frequency","Output_Current","Output_Voltage","AC_Power"]]
    
    for i in range(len(server)):
        try:
            server[i].send_command(command="read",address=addr[i])
        except Exception as e:
            # Print the error message
            print("(modbus) problem with",server[i]._name,":")
            print(e)
            print("<===== ===== continuing ===== =====>")
            print("")
            
def write_modbus(server):
    #return
    for i in range(len(server)):
        try:
            pass
        except Exception as e:
            # Print the error message
            print("(modbus) problem with",server[i]._name,":")
            print(e)
            print("<===== ===== continuing ===== =====>")
            print("")

def send_sync_request_socket():
    """
    Send a synchronization request to the server.
    """
    try:
        # AF_UNIX
        unix_address = '/tmp/ipc_socket'
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(unix_address)
        
        #AF_INET
        #inet_address = ('127.0.0.1', 9000)
        #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client_socket.connect(inet_address)

        # Send sync request
        client_socket.send(b"sync_request")

        # Wait for acknowledgment from server
        ack = client_socket.recv(1024).decode('utf-8') 
        if ack == "ack":
            # If acknowledgment is received, wait for SYNC_WAIT_TIME before actual data transfer.
            time.sleep(SYNC_WAIT_TIME)
            return True
        else:
            client_socket.close()
            return False
    except socket.error as e:
        print(f"(socket) Error: {e}")
        return False
    except Exception as e:
        print(f"(socket) General Error in send_sync_request_socket: {e}")
        return False

def send_data_socket(raw_data):
    try:
        data_str = ','.join(map(str,raw_data))
        processed_data = data_str.encode('utf-8')
        unix_address = '/tmp/ipc_socket'
        #inet_address = ('127.0.0.1', 9000)
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(unix_address)
        #client_socket.connect(inet_address)
        print(data_str)
        client_socket.send(processed_data)
        
        # Receive acknowledgment from server
        ack = client_socket.recv(1024).decode('utf-8')  # assuming 'ack' message is within 1024 bytes
        print("(socket) Received from server:", ack)

        client_socket.close()
        return ack
    except socket.error as e:
        print(f"(socket) Error: {e}")
        return None
    except Exception as e:
        print(f"(socket) General Error in send_data_socket: {e}")
        return None
        
def data_processing(server, timer):
    cpu_temp = query.get_cpu_temperature()
    
    title = ["time","cpu_Temp","bat_Temp",
             "bat_soc","bat_ttl_V","bat_avg_V",
             "con_out_V_ref","con_in_V","con_in_A",
             "con_out_kW","con_in_Hz","con_in_PF",
             "con_in_kW","con_consume_kWh","con_produce_kWh",
             "inv_out_Hz","inv_out_A","inv_out_V_ref","inv_out_kWh"]
    
    data = [timer.strftime("%Y-%m-%d %H:%M:%S"), cpu_temp, server[1].Temperature_avg,
            server[1].SOC, server[1].Total_Voltage, server[1].Cell_Voltage_avg,
            server[0].DC_Voltage_Command, server[0].AC_Voltage, server[0].AC_Current,
            server[0].DC_Power, server[0].AC_Frequency, server[0].Power_Factor,
            server[0].AC_Power, server[0].Consumed_Power_kWh, server[0].Produced_Power_kWh,
            server[2].Output_Frequency, server[2].Output_Current, server[2].Output_Voltage, server[2].AC_Power]
    
    return title, data

def update_database(title, data, timer):
    global mysql_server
    # Define MySQL queries and data which will be used in the program
    cpu_temp = query.get_cpu_temperature()
    mysql_query = ("INSERT INTO `{}` ({}) VALUES ({})".format(mysql_server["table"],
                                                                ",".join(title),
                                                                ",".join(['%s' for _ in range(len(title))])))
    filename = 'modbus_log.csv'

    query.log_in_csv(title ,data, timer, filename)
    query.retry_mysql(mysql_server, mysql_query, filename, mysql_timeout)

#################################################################################################################
def main():
    init = True  # variable to check Modbus initialization
    # Checking the connection Modbus
    while init:
        try:
            # Setup Raspberry Pi as Modbus client/master
            server = setup_modbus()
            logging.info("Connected to Modbus Communication")
            #print("<===== Connected to Modbus Communication =====>")
            #print("")
            init = False
        except Exception as e:
            # Print the error message
            logging.error("(modbus) Problem with Modbus communication: %s", e)
            #print("<===== ===== retrying ===== =====>")
            #print("")
            time.sleep(3)

    first = [True, True]
    # Reading a Modbus message and Upload to database sequence
    while not init:
        try:
            # First run (start-up) sequence
            if first[0]:
                first[0] = False
                # time counter
                start = datetime.datetime.now()
                write_modbus(server)
            
            # Send the command to read the measured value and do all other things
            read_modbus(server)
            timer = datetime.datetime.now()
            query.print_response(server, timer)
            title, data = data_processing(server, timer)
        
            #Send data to other script for display purpose
            acknowledgment = threading.Thread(target=send_data_socket, args=(data,)).start()

            # Check elapsed time
            if (timer - start).total_seconds() > mysql_interval or first[1] == True:
                start = timer
                first[1] = False
                # Update/push data to database
                update_database(title, data, timer)
        
            if acknowledgment == 'ack':
                print("(socket) Data successfully received by the server!")
            else:
                print("(socket) There was an issue sending the data or acknowledgment was not received.")
            time.sleep(interval)
    
        except Exception as e:
            # Print the error message
            logging.error("Encountered an error: %s", e)
            #print(e)
            #print("<===== ===== retrying ===== =====>")
            #print("")
            time.sleep(3)
            
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down client.")
        # Ensure resources are closed properly.
