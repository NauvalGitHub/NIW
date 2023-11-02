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
from pymodbus.client import ModbusSerialClient as ModbusClient
import query
from lib import kyuden_battery_72kWh as battery
from lib import yaskawa_D1000 as converter
from lib import yaskawa_GA500 as inverter
#from lib import tristar_MPPT as charger

# Define Modbus communication parameters
port            = '/dev/ttyAMA0'    # for RS485/CAN Hat
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
#mysql_server    = {"host":"http://machinedatanglobal.c4sty2dpq6yv.ap-northeast-1.rds.amazonaws.com",
#                    "user":"Nglobal_root_NIW",
#                    "password": "Niw_Machinedata_11089694",
#                    "db":"NEPOWER_XX",
#                    "table":"dataparameter",
#                    "port":3306}
mysql_server    = {"host":"10.4.171.204",
                   "user":"root",
                    "password":"niw2082023",
                    "db":"test",
                    "table":"not_used",
                    "port":3306}
mysql_timeout   = 3 # the maximum time this device will wait for completing MySQl query (in seconds)
mysql_interval  = 300 # the period between each subsequent update to database (in seconds)

#query.debugging()  # Monitor Modbus communication for debugging
init = True  # variable to check Modbus initialization

def setup_modbus():
    global port, port0, method, bytesize, stopbits, parity, baudrate, client_latency, timeout
    # Set each Modbus communication port specification
    client = ModbusClient(port=port, method=method, stopbits=stopbits, bytesize=bytesize, parity=parity, baudrate=baudrate, timeout=timeout)
    client0 = ModbusClient(port=port0, method=method, stopbits=stopbits, bytesize=bytesize, parity=parity, baudrate=baudrate, timeout=timeout)
    # Connect to the Modbus serial
    client.connect()
    client0.connect()
    # Define the Modbus slave/server (nodes) objects
    bat = battery.node(unit=1, name='BATTERY', client=client0, delay=client_latency, max_count=20, increment=1, shift=0)
    conv = converter.node(unit=2, name='CONVERTER', client=client, delay=client_latency, max_count=20, increment=1, shift=0)
    inv = inverter.node(unit=3, name='INVERTER', client=client, delay=client_latency, max_count=20, increment=1, shift=0)
    #chr = charger.node(unit=4, name='SOLAR CHARGER', client=client, delay=client_latency)
    server = [bat, conv, inv]
    #server = [conv, inv]
    return server

def read_modbus(server):
    addr=[["SOC","Total_Voltage","Cell_Voltage_avg","Temperature_avg"],
          ["DC_Voltage_Command","AC_Voltage","AC_Current","DC_Power","AC_Frequency","Power_Factor","AC_Power","Consumed_Power_kWh","Produced_Power_kWh"],
          ["Output_Frequency","Output_Current","Output_Voltage","AC_Power"]]
    
    #addr=[["DC_Voltage_Command","AC_Voltage","AC_Current","DC_Power","AC_Frequency","Power_Factor","AC_Power","Consumed_Power_kWh","Produced_Power_kWh"],
    #      ["Output_Frequency","Output_Current","Output_Voltage","AC_Power"]]
    
    for i in range(len(server)):
        try:
            server[i].send_command(command="read",address=addr[i])
        except Exception as e:
            # Print the error message
            print("problem with",server[i]._name,":")
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
            print("problem with",server[i]._name,":")
            print(e)
            print("<===== ===== continuing ===== =====>")
            print("")

def send_data_socket(raw_data):
    try:
        data_str = ','.join(map(str,raw_data))
        processed_data = data_str.encode('utf-8')
        unix_address = '/tmp/ipc_socket'
        inet_address = ('127.0.0.1', 9000)
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) #socket.AF_UNIX or socket.AF_INET
        client_socket.connect(unix_address)
        #client_socket.connect(inet_address)
        print(data_str)
        client_socket.send(processed_data)
        client_socket.close()
    except socket.error as e:
        print("Error: Unable to connect to the server.")
        
def data_processing(server, timer):
    cpu_temp = query.get_cpu_temperature()
    
    title = ["dataentered","CPU_temp","avg_temp",
             "soc","total_vol","cell_avg_vol",
             "dc_bus_v_ref","power_supply_vol","power_supply_current",
             "dc_bus_side_power","power_supply_freq","power_factor",
             "power_supply_side_power","electric_power_kwh","regene_power_kwh",
             "out_freq","out_current","out_vol_ref","out_power"]
    
    #title = ["dataentered","CPU_temp",
    #         "dc_bus_v_ref","power_supply_vol","power_supply_current",
    #         "dc_bus_side_power","power_supply_freq","power_factor",
    #         "power_supply_side_power","electric_power_kwh","regene_power_kwh",
    #         "out_freq","out_current","out_vol_ref","out_power"]
    
    data = [timer.strftime("%Y-%m-%d %H:%M:%S"), cpu_temp, server[0].Temperature_avg,
            server[0].SOC, server[0].Total_Voltage, server[0].Cell_Voltage_avg,
            server[1].DC_Voltage_Command, server[1].AC_Voltage, server[1].AC_Current,
            server[1].DC_Power, server[1].AC_Frequency, server[1].Power_Factor,
            server[1].AC_Power, server[1].Consumed_Power_kWh, server[1].Produced_Power_kWh,
            server[2].Output_Frequency, server[2].Output_Current, server[2].Output_Voltage, server[2].AC_Power]
    
    #data = [timer.strftime("%Y-%m-%d %H:%M:%S"), cpu_temp,
    #        server[0].DC_Voltage_Command, server[0].AC_Voltage, server[0].AC_Current,
    #        server[0].DC_Power, server[0].AC_Frequency, server[0].Power_Factor,
    #        server[0].AC_Power, server[0].Consumed_Power_kWh, server[0].Produced_Power_kWh,
    #        server[1].Output_Frequency, server[1].Output_Current, server[1].Output_Voltage, server[1].AC_Power]
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

# Checking the connection Modbus
while init:
    try:
        # Setup Raspberry Pi as Modbus client/master
        server = setup_modbus()
        print("<===== Connected to Modbus Communication =====>")
        print("")
        init = False
    except Exception as e:
        # Print the error message
        print("problem with Modbus communication:")
        print(e)
        print("<===== ===== retrying ===== =====>")
        print("")
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
        threading.Thread(target=send_data_socket, args=(data,)).start()

        # Check elapsed time
        if (timer - start).total_seconds() > mysql_interval or first[1] == True:
            start = timer
            first[1] = False
            # Update/push data to database
            update_database(title, data, timer)
        
        time.sleep(interval)
    
    except Exception as e:
        # Print the error message
        print(e)
        print("<===== ===== retrying ===== =====>")
        print("")
        time.sleep(3)
