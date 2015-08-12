#!/usr/bin/env python

import subprocess, os, re, sqlite3

battery_current = battery_voltage = battery_power_operating = battery_power_charging = 0
mc_cap_voltage = heatsink_temp = current_fault = traction_state = motor_temp = motor_current = 0
motor_voltage = mc_battery_current = vehicle_speed = motor_velocity = max_batt_discharge_current = max_batt_charge_current = 0
soc = isPluggedIn = isCharging = isOperating = isRunning = 0
torque = status_word = 0
connected = False

previous_date = ""
previous_time = 0

logsPath = "/data/databases/GroundHogLogs.db"

def twos_comp(val, bits):
    #compute the 2's compliment of int value val
    val = int(val)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

def parse_data(msg_id, data):
    global battery_current, battery_voltage, torque, status_word, mc_cap_voltage, heatsink_temp, motor_temp, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp
    global isPluggedIn, isCharging, isOperating, isRunning
    
    pattern = re.compile(r'\s+')
    data = re.sub(pattern, '', data)
    
    if (msg_id == "201" or msg_id == "202" or msg_id == "203"):
        status_word = data[2] + data[3] + data[0] + data[1]

        mc_cap_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/16.0

        battery_voltage = int(data[10] + data[11] + data[8] + data[9], 16)/16.0

        print msg_id +  ": " + status_word + ", " + `mc_cap_voltage` + ", " + `battery_voltage`

    if (msg_id == "301" or msg_id == "302" or msg_id == "303"):
        motor_velocity = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16) #Something special needs to be done with this
        motor_velocity = twos_comp(motor_velocity, 32)

        if (motor_velocity > 0.125 or motor_velocity < 0.125):
            isRunning = 1

        motor_temp = int(data[10] + data[11] + data[8] + data[9], 16)

        print msg_id + ": " + `motor_velocity` + ", " + `motor_temp`
	
    if (msg_id == "401" or msg_id == "402" or msg_id == "403"):

        isOperating = 1
        
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0

        if (battery_current) > 0.1:
            isCharging = 1
        
        motor_current = int(data[6] + data[7] + data[4] + data[5], 16)

        torque = int(data[10] + data[11] + data[8] + data[9], 16)

        heatsink_temp = int(data[12] + data[13], 16)

        print msg_id +  ": " + `battery_current` + ", " + `motor_current` + ", " + `torque` + ", " + `heatsink_temp`

#connect to databases
if (not connected):
    logsDB=sqlite3.connect(logsPath)
    logsCurs=logsDB.cursor()
    connected = True

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

    #write values to dailylogs database
    command = "INSERT INTO logs values('"

    command += current_date[0:10] + "','"
    command += current_date[11:24] + "','"
    
    command += status_word + "','"
    command += `mc_cap_voltage` + "','"        
    command += `battery_voltage` + "','"

    command += `motor_velocity` + "','"
    command += `motor_temp` + "','"

    command += `battery_current` + "','"
    command += `motor_current` + "','"
    command += `torque` + "','"
    command += `heatsink_temp` + "','0','0','0');"

    print current_date[0:10] + "  " + current_date[11:24] + "\n"
##    print "20X: " + `status_word` + ", " + `mc_cap_voltage` + ", " + `battery_voltage`
##    print "30X: " + `motor_velocity` + ", " + `motor_temp`
##    print "40X: " + `battery_current` + ", " + `motor_current` + ", " + `torque` + ", " + `heatsink_temp`
##    print ""

    logsCurs.execute(command)
    logsDB.commit()

    #zero all data
    battery_current = battery_voltage = motor_current = 0
    motor_voltage = mc_cap_voltage = motor_velocity = 0
    motor_temp = heatsink_temp = status_word = torque = 0
    #isOperating = isCharging = isRunning =  0
        
###close databases
##logsDB.close()
