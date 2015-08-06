#!/usr/bin/env python

import subprocess, os, re, sqlite3

battery_current = battery_voltage = battery_power_operating = battery_power_charging = 0
mc_cap_voltage = heatsink_temp = current_fault = traction_state = motor_temp = motor_current = 0
motor_voltage = mc_battery_current = vehicle_speed = motor_velocity = max_batt_discharge_current = max_batt_charge_current = 0
soc = isPluggedIn = isCharging = isOperating = isRunning = 0
batt_high_temp = batt_low_temp = batt_high_temp_id = batt_low_temp_id = 0

odometer = hours_plugged_in = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = motor_energy = aux_energy = 0

previous_date = ""
previous_time = 0

logsPath = "/data/databases/Logs.db"

def twos_comp(val, bits):
    #compute the 2's compliment of int value val
    val = int(val)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

def parse_data(msg_id, data):
    global battery_current, battery_voltage, battery_power_operating, battery_power_charging
    global mc_cap_voltage, heatsink_temp, current_fault, traction_state, motor_temp, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp, odometer, hours_plugged_in, hours_charging, hours_operating, hours_running, battery_energy_operating, battery_energy_charging
    global max_batt_discharge_current, max_batt_charge_current
    global soc, isPluggedIn, isCharging, isOperating, isRunning
    global batt_high_temp, batt_low_temp, batt_high_temp_id, batt_low_temp_id
    
    pattern = re.compile(r'\s+')
    data = re.sub(pattern, '', data)
    
    if (msg_id == "477"):
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_operating = battery_current * battery_voltage / 1000.0
        if (isCharging):
            battery_power_operating = 0 #don't show current in operating, it's going to be in charging

        soc = int(data[10] + data[11] + data[8] + data[9], 16)/2
        
        data_6 = str(bin(int(data[12] + data[13], 16)))[2:]
        while (len(data_6) < 8):
            data_6 = '0' + data_6
        isOperating = 1  

    elif (msg_id == "478"):     # same as 477 but on charge
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0

        if (battery_current) > 0.1:
            isCharging = 1
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_charging = battery_current * battery_voltage / 1000.0

        soc = int(data[10] + data[11] + data[8] + data[9], 16)/2
        
        data_6 = str(bin(int(data[12] + data[13], 16)))[2:]
        while (len(data_6) < 8):
            data_6 = '0' + data_6
        isPluggedIn = 1

    elif (msg_id == "479" or msg_id == "480"):     # these two transmit the same info
        batt_high_temp = int(data[0] + data[1], 16)
        batt_low_temp = int(data[4] + data[5], 16)
        batt_high_temp_id = int(data[8] + data[9], 16)
        batt_low_temp_id = int(data[10] + data[11], 16)

    elif (msg_id == "475"):
        mc_cap_voltage = int(data[2] + data[3] + data[0] + data[1], 16)/16.0
        heatsink_temp = int(data[4] + data[5], 16)

        fault = str(int(data[8] + data[9] + data[6] + data[7], 16))
        if fault not in str(current_fault):
            if current_fault != 0:
                current_fault += ", "
            current_fault += fault
        
        traction_state = int(data[10] + data[11], 16)
        motor_current = int(data[14] + data[15] + data[12] + data[13], 16)

    elif (msg_id == "270"):
        motor_voltage = int(data[14] + data[15] + data[12] + data[13], 16) * 0.0625

    elif (msg_id == "294"):
        max_batt_charge_current = int(data[6] + data[7] + data[4] + data[5], 16)
        max_batt_charge_current = twos_comp(max_batt_charge_current, 16)
        max_batt_discharge_current = int(data[10] + data[11] + data[8] + data[9], 16)
        mc_battery_current = int(data[14] + data[15] + data[12] + data[13], 16)
        mc_battery_current = twos_comp(mc_battery_current, 16)
        mc_battery_current = mc_battery_current * 0.0625

    elif (msg_id == "306"):
        motor_temp = int(data[2] + data[3] + data[0] + data[1], 16)
        vehicle_speed = int(data[6] + data[7] + data[4] + data[5], 16)
        vehicle_speed = twos_comp(vehicle_speed, 16)
        isNegative = False
        if (vehicle_speed < 0):
            isNegative = True
        str_vs = str(bin(vehicle_speed))[2:]
        if isNegative:
            str_vs = str_vs[1:] #get rid of an extra digit because of the '-'
        while (len(str_vs) < 16):
            str_vs = '0' + str_vs
        vehicle_speed = int(str_vs[0:-4],2) + (0.0625 * int(str_vs[-4:],2)) #Convert to 12.4 format.
        if isNegative:
            vehicle_speed *= -1
        motor_velocity = int(data[14] + data[15] + data[12] + data[13] + data[10] + data[11] + data[8] + data[9], 16) #Something special needs to be done with this
        motor_velocity = twos_comp(motor_velocity, 32)

        if vehicle_speed <= -0.062 or vehicle_speed >= 0.062:
            isRunning = 1
        else:
            isRunning = 0

#connect to databases
logsDB=sqlite3.connect(logsPath)
logsCurs=logsDB.cursor()

while (True): #Checks the date, starts logging, when the logging ends (end of day, or end of time-period) it will transfer data to permanent location.
            
    #get x messages
    p = subprocess.Popen("./candump -t A -n 10 can0,477:7ff,478:7ff,479:7ff,480:7ff,475:7ff,270:7ff,294:7ff,306:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
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
    p = subprocess.Popen("date +\"%Y-%m-%d %H:%M:%S\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    current_date = output
    
    #calculate time difference between current and previous time stamps
    times = current_date[11:19].split(":")
    current_time = int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2]) #convert to seconds
    time_span = 1 #if there is no previous time stamp, assume 1s
    if previous_time is not None:
        time_span = (current_time - previous_time)
        if time_span > 2: #if time between time stamps is too long, assume 1s
            time_span = 1
    previous_time = current_time
    previous_date = current_date
        
    #if less than a second
    if time_span >= 1:

        #write values to dailylogs database
        command = "INSERT INTO dailyLogs values('"

        command += current_date[0:10] + "','"
        command += current_date[11:19] + "','"
        command += `soc` + "','"
        command += `battery_current` + "','"
        command += `battery_voltage` + "','"
        
        command += `battery_power_operating` + "','"
        command += `battery_power_charging` + "','"
        
        command += `motor_current` + "','"
        command += `motor_voltage` + "','"
        
        command += `mc_battery_current` + "','"
        command += `mc_cap_voltage` + "','"
        
        command += `vehicle_speed` + "','"
        command += `motor_velocity` + "','"
        
        command += `current_fault` + "','"
        command += `traction_state` + "','"
        
        command += `max_batt_discharge_current` + "','"
        command += `max_batt_charge_current` + "','"
        
        command += `motor_temp` + "','"
        command += `heatsink_temp` + "','"
        
        command += `batt_high_temp` + "','"
        command += `batt_high_temp_id` + "','"
        command += `batt_low_temp` + "','"
        command += `batt_low_temp_id` + "','"
        
        command += `isPluggedIn` + "','"
        command += `isCharging` + "','"
        command += `isOperating` + "','"
        command += `isRunning`
    
        command += "');"
        
        logsCurs.execute(command)
        logsDB.commit()

        #integrate certain variables over time to gets sums
        odometer = (vehicle_speed * time_span)/3600.0
        hours_plugged_in = (isPluggedIn * time_span)/3600.0
        hours_charging = (isCharging * time_span)/3600.0
        hours_operating = (isOperating * time_span)/3600.0
        hours_running = (isRunning  * time_span)/3600.0
        battery_energy_operating = (battery_power_operating * time_span)/3600.0
        battery_energy_charging = (battery_power_charging * time_span)/3600.0

        #retrieve old summary data if it exists
        logsCurs.execute("SELECT * FROM summary WHERE date='" + current_date[0:10] + "' LIMIT 1;")
        oldSummaryData = logsCurs.fetchall()[0]

        if len(oldSummaryData) > 0:
            for datum in oldSummaryData:
                odometer += float(oldSummaryData[1])
                hours_plugged_in += float(oldSummaryData[2])
                hours_charging += float(oldSummaryData[3])
                hours_operating += float(oldSummaryData[4])
                hours_running += float(oldSummaryData[5])
                battery_energy_operating += float(oldSummaryData[6])
                battery_energy_charging += float(oldSummaryData[7])

            #update summary data in database
            command = "UPDATE summary SET odometer="
            command += `odometer` + ",hours_plugged_in="
            command += `hours_plugged_in` + ",hours_charging="
            command += `hours_charging` + ",hours_operating="
            command += `hours_operating` + ",hours_running="
            command += `hours_running` + ",energy_out="
            command += `battery_energy_operating` + ",energy_in="
            command += `battery_energy_charging`
            command += " WHERE date='" + current_date[0:10] + "';" 
            
        else:
            #insert summary data into database
            command = "INSERT INTO summary VALUES('"
            command += current_date[0:10] + "','"
            command += `odometer` + "','"
            command += `hours_plugged_in` + "','"
            command += `hours_charging` + "','"
            command += `hours_operating` + "','"
            command += `hours_running` + "','"
            command += `battery_energy_operating` + "','"
            command += `battery_energy_charging`
            command += "');"

        logsCurs.execute(command)
        logsDB.commit()

        #zero all data
        battery_current = battery_voltage = battery_power_operating = battery_power_charging = motor_current = 0
        motor_voltage = mc_cap_voltage = current_fault = traction_state = vehicle_speed = motor_velocity = soc = 0
        max_batt_discharge_current = max_batt_charge_current = motor_temp = heatsink_temp = batt_high_temp = batt_high_temp_id = 0
        batt_low_temp = batt_low_temp_id = isPluggedIn = isCharging = isOperating = isRunning = 0
        odometer = hours_plugged_in = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = 0
        
#close databases
logsDB.close()
