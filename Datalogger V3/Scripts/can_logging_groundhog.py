#!/usr/bin/env python

import subprocess, os, re, sqlite3

battery_current = battery_voltage = [0,0,0]
mc_cap_voltage = heatsink_temp = motor_temp = motor_current = [0,0,0]
motor_voltage = mc_battery_current = motor_velocity = [0,0,0]
torque = status_word = [0,0,0]
connected = False

previous_date = ""
previous_time = 0

logsPath = "/data/databases/GroundHogLogs.csv"

def twos_comp(val, bits):
    #compute the 2's compliment of int value val
    val = int(val)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

def parse_data(msg_id, data):
    global battery_current, battery_voltage, torque, status_word, mc_cap_voltage, heatsink_temp, motor_temp, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp
    
    pattern = re.compile(r'\s+')
    data = re.sub(pattern, '', data)
    
    if (msg_id == "201" or msg_id == "202" or msg_id == "203"):
        i = int(msg_id[2])-1
        status_word[i] = data[2] + data[3] + data[0] + data[1]

        mc_cap_voltage[i] = int(data[6] + data[7] + data[4] + data[5], 16)/16.0

        battery_voltage[i] = int(data[10] + data[11] + data[8] + data[9], 16)/16.0

        print msg_id +  ": " + status_word[i] + ", " + `mc_cap_voltage[i]` + ", " + `battery_voltage[i]`

    if (msg_id == "301" or msg_id == "302" or msg_id == "303"):
        i = int(msg_id[2])-1
        motor_velocity[i] = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16) #Something special needs to be done with this
        motor_velocity[i] = twos_comp(motor_velocity[i], 32)

        motor_temp[i] = int(data[10] + data[11] + data[8] + data[9], 16)

        print msg_id + ": " + `motor_velocity[i]` + ", " + `motor_temp[i]`
	
    if (msg_id == "401" or msg_id == "402" or msg_id == "403"):
        i = int(msg_id[2])-1
        
        battery_current[i] = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current[i] = twos_comp(battery_current[i], 16)
        battery_current[i] /= 10.0
        
        motor_current[i] = int(data[6] + data[7] + data[4] + data[5], 16)

        torque[i] = int(data[10] + data[11] + data[8] + data[9], 16)

        heatsink_temp[i] = int(data[12] + data[13], 16)

        print msg_id +  ": " + `battery_current[i]` + ", " + `motor_current[i]` + ", " + `torque[i]` + ", " + `heatsink_temp[i]`

while (True): #Checks the date, starts logging, when the logging ends (end of day, or end of time-period) it will transfer data to permanent location.
            
    #get x messages
    p = subprocess.Popen("./candump -t A -n 9 can0,201:7ff,202:7ff,203:7ff,301:7ff,302:7ff,303:7ff,401:7ff,402:7ff,403:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    lines = output.strip().split("\n")
    
    #parse messages
    for line in lines:
##        try:
        data = line.strip().split("  ")
        parse_data(data[2], data[3][3:].strip()) #message id, message
##        except:
##            print "Error parsing line: " + line
##            pass

    #get date & time
    p = subprocess.Popen("date +\"%Y-%m-%d %H:%M:%S:%N\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    current_date = output
    
    #calculate time difference between current and previous time stamps
    times = current_date[11:24].split(":")

    #write values to excel
    excelFile = open(logsPath, 'a+')

    excelFile.write(current_date[0:10] + ",") 
    excelFile.write(current_date[11:24] + ",")

    for i in range(0,3):
        excelFile.write(status_word[i] + ",")
        excelFile.write(`mc_cap_voltage[i]` + ",")        
        excelFile.write(`battery_voltage[i]` + ",")

        excelFile.write(`motor_velocity[i]` + ",")
        excelFile.write(`motor_temp[i]` + ",")

        excelFile.write(`battery_current[i]` + ",")
        excelFile.write(`motor_current[i]` + ",")
        excelFile.write(`torque[i]` + ",")
        excelFile.write(`heatsink_temp[i]` + ",")

    excelFile.write("\n")
    excelFile.close()

    print current_date[0:10] + "  " + current_date[11:24] + "\n"
    
    #zero all data
    battery_current = battery_voltage = motor_current = [0,0,0]
    motor_voltage = mc_cap_voltage = motor_velocity = [0,0,0]
    motor_temp = heatsink_temp = status_word = torque = [0,0,0]
        
###close databases
##logsDB.close()
