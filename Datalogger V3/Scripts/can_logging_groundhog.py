#!/usr/bin/env python

import subprocess, os, re, sqlite3

battery_current1 = battery_voltage1 = mc_cap_voltage1 = heatsink_temp1 = motor_temp1 = motor_current1 = motor_voltage1 = mc_battery_current1 = motor_velocity1 = torque1 = 0
status_word1 = ""

battery_current2 = battery_voltage2 = mc_cap_voltage2 = heatsink_temp2 = motor_temp2 = motor_current2 = motor_voltage2 = mc_battery_current2 = motor_velocity2 = torque2 = 0
status_word2 = ""

battery_current3 = battery_voltage3 = mc_cap_voltage3 = heatsink_temp3 = motor_temp3 = motor_current3 = motor_voltage3 = mc_battery_current3 = motor_velocity3 = torque3 = 0
status_word3 = ""

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
    global status_word1, battery_current1, battery_voltage1, mc_cap_voltage1, heatsink_temp1, motor_temp1, motor_current1, motor_voltage1, mc_battery_current1, vehicle_speed1, motor_velocity1, torque1
    global status_word2, battery_current2, battery_voltage2, mc_cap_voltage2, heatsink_temp2, motor_temp2, motor_current2, motor_voltage2, mc_battery_current2, vehicle_speed2, motor_velocity2, torque2
    global status_word3, battery_current3, battery_voltage3, mc_cap_voltage3, heatsink_temp3, motor_temp3, motor_current3, motor_voltage3, mc_battery_current3, vehicle_speed3, motor_velocity3, torque3
    global last_time_stamp

    pattern = re.compile(r'\s+')
    data = re.sub(pattern, '', data)

    if (msg_id == "201"):
        status_word1 = str(data[2] + data[3] + data[0] + data[1])

        mc_cap_voltage1 = int(data[6] + data[7] + data[4] + data[5], 16)/16.0

        battery_voltage1 = int(data[10] + data[11] + data[8] + data[9], 16)/16.0

    if (msg_id == "202"):
        status_word2 = str(data[2] + data[3] + data[0] + data[1])

        mc_cap_voltage2 = int(data[6] + data[7] + data[4] + data[5], 16)/16.0

        battery_voltage2 = int(data[10] + data[11] + data[8] + data[9], 16)/16.0

    if (msg_id == "203"):
        status_word3 = str(data[2] + data[3] + data[0] + data[1])

        mc_cap_voltage3 = int(data[6] + data[7] + data[4] + data[5], 16)/16.0

        battery_voltage3 = int(data[10] + data[11] + data[8] + data[9], 16)/16.0	

    if (msg_id == "301"):
        motor_velocity1 = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16) #Something special needs to be done with this
        motor_velocity1 = twos_comp(motor_velocity1, 32)

        motor_temp1 = int(data[10] + data[11] + data[8] + data[9], 16)

    if (msg_id == "302"):
        motor_velocity2 = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16) #Something special needs to be done with this
        motor_velocity2 = twos_comp(motor_velocity2, 32)

        motor_temp2 = int(data[10] + data[11] + data[8] + data[9], 16)

    if (msg_id == "303"):
        motor_velocity3 = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16) #Something special needs to be done with this
        motor_velocity3 = twos_comp(motor_velocity3, 32)

        motor_temp3 = int(data[10] + data[11] + data[8] + data[9], 16)

    if (msg_id == "401"):

        battery_current1 = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current1 = twos_comp(battery_current1, 16)
        battery_current1 /= 10.0

        motor_current1 = int(data[6] + data[7] + data[4] + data[5], 16)

        torque1 = int(data[10] + data[11] + data[8] + data[9], 16)

        heatsink_temp1 = int(data[12] + data[13], 16)

    if (msg_id == "402"):

        battery_current2 = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current2 = twos_comp(battery_current2, 16)
        battery_current2 /= 10.0

        motor_current2 = int(data[6] + data[7] + data[4] + data[5], 16)

        torque2 = int(data[10] + data[11] + data[8] + data[9], 16)

        heatsink_temp2 = int(data[12] + data[13], 16)

    if (msg_id == "403"):

        battery_current3 = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current3 = twos_comp(battery_current3, 16)
        battery_current3 /= 10.0

        motor_current3 = int(data[6] + data[7] + data[4] + data[5], 16)

        torque3 = int(data[10] + data[11] + data[8] + data[9], 16)

        heatsink_temp3 = int(data[12] + data[13], 16)     

while (True): #Checks the date, starts logging, when the logging ends (end of day, or end of time-period) it will transfer data to permanent location.

    #get x messages
    p = subprocess.Popen("./candump -t A -n 9 can0,201:7ff,202:7ff,203:7ff,301:7ff,302:7ff,303:7ff,401:7ff,402:7ff,403:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    lines = output.strip().split("\n")

    #parse messages
    for line in lines:
        try:
        data = line.strip().split("  ")
        parse_data(data[2], data[3][3:].strip()) #message id, message
        except:
            print "Error parsing line: " + line
            pass

    #get date & time
    p = subprocess.Popen("date +\"%Y-%m-%d %H:%M:%S:%N\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    current_date = output

    #calculate time difference between current and previous time stamps
    times = current_date[11:24].split(":")

    #write values to excel
    excelFile = open(logsPath, 'a+')
    
    if (not connected):
    	excelFile.write("\nDate, Time, Status Word, Cap Voltage, Battery Voltage, Motor Velocity, Motor Temp, Battery Current, Motor Current, Torque, Heatsink Temp, , Status Word, Cap Voltage, Battery Voltage, Motor Velocity, Motor Temp, Battery Current, Motor Current, Torque, Heatsink Temp, , Status Word, Cap Voltage, Battery Voltage, Motor Velocity, Motor Temp, Battery Current, Motor Current, Torque, Heatsink Temp\n")
        connected = True    

    #write to screen
    print current_date[0:10] + "  " + current_date[11:24] + "\n"
    
    print "201: " + status_word1 + ", " + `mc_cap_voltage1` + ", " + `battery_voltage1`
    print "202: " + status_word2 + ", " + `mc_cap_voltage2` + ", " + `battery_voltage2`
    print "203: " + status_word3 + ", " + `mc_cap_voltage3` + ", " + `battery_voltage3`

    print "301: " + `motor_velocity1` + ", " + `motor_temp1`
    print "302: " + `motor_velocity2` + ", " + `motor_temp2`
    print "303: " + `motor_velocity3` + ", " + `motor_temp3`

    print "401: " + `battery_current1` + ", " + `motor_current1` + ", " + `torque1` + ", " + `heatsink_temp1`
    print "402: " + `battery_current2` + ", " + `motor_current2` + ", " + `torque2` + ", " + `heatsink_temp2`
    print "403: " + `battery_current3` + ", " + `motor_current3` + ", " + `torque3` + ", " + `heatsink_temp3`

    #write to file
    excelFile.write(current_date[0:10] + ",")
    excelFile.write(current_date[11:24] + ",")

    excelFile.write(status_word1 + ",")
    excelFile.write(`mc_cap_voltage1` + ",")
    excelFile.write(`battery_voltage1` + ",")

    excelFile.write(`motor_velocity1` + ",")
    excelFile.write(`motor_temp1` + ",")

    excelFile.write(`battery_current1` + ",")
    excelFile.write(`motor_current1` + ",")
    excelFile.write(`torque1` + ",")
    excelFile.write(`heatsink_temp1` + ", ,")


    excelFile.write(status_word2 + ",")
    excelFile.write(`mc_cap_voltage2` + ",")
    excelFile.write(`battery_voltage2` + ",")

    excelFile.write(`motor_velocity2` + ",")
    excelFile.write(`motor_temp2` + ",")

    excelFile.write(`battery_current2` + ",")
    excelFile.write(`motor_current2` + ",")
    excelFile.write(`torque2` + ",")
    excelFile.write(`heatsink_temp2` + ", ,")


    excelFile.write(status_word3 + ",")
    excelFile.write(`mc_cap_voltage3` + ",")
    excelFile.write(`battery_voltage3` + ",")

    excelFile.write(`motor_velocity3` + ",")
    excelFile.write(`motor_temp3` + ",")

    excelFile.write(`battery_current3` + ",")
    excelFile.write(`motor_current3` + ",")
    excelFile.write(`torque3` + ",")
    excelFile.write(`heatsink_temp3` + ", ,")

    excelFile.write("\n")
    excelFile.close()


    #zero all data
    battery_current1 = battery_voltage1 = mc_cap_voltage1 = heatsink_temp1 = motor_temp1 = motor_current1 = motor_voltage1 = mc_battery_current1 = motor_velocity1 = torque1 = 0
    status_word1 = ""

    battery_current2 = battery_voltage2 = mc_cap_voltage2 = heatsink_temp2 = motor_temp2 = motor_current2 = motor_voltage2 = mc_battery_current2 = motor_velocity2 = torque2 = 0
    status_word2 = ""

    battery_current3 = battery_voltage3 = mc_cap_voltage3 = heatsink_temp3 = motor_temp3 = motor_current3 = motor_voltage3 = mc_battery_current3 = motor_velocity3 = torque3 = 0
    status_word3 = ""
