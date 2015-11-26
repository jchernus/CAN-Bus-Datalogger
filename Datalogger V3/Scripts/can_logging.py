#!/usr/bin/env python

import subprocess, os, re, sqlite3

battery_current = battery_voltage = battery_power_operating = battery_power_charging = 0
mc_cap_voltage = heatsink_temp = active_fault = traction_state = motor_temp = motor_current = 0
motor_voltage = mc_battery_current = vehicle_speed = motor_velocity = DCL = CCL = 0
soc = isPluggedIn = isCharging = isOperating = isRunning = 0
batt_high_temp = batt_low_temp = batt_high_temp_id = batt_low_temp_id = 0
high_cell_voltage = low_cell_voltage = high_cell_voltage_id = low_cell_voltage_id = 0

odometer = hours_plugged_in = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = motor_energy = aux_energy = 0

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
    global mc_cap_voltage, heatsink_temp, active_fault, traction_state, motor_temp, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp, odometer, hours_plugged_in, hours_charging, hours_operating, hours_running, battery_energy_operating, battery_energy_charging
    global DCL, CCL, batt_high_temp, batt_low_temp, batt_high_temp_id, batt_low_temp_id
    global high_cell_voltage, low_cell_voltage, high_cell_voltage_id, low_cell_voltage_id
    global soc, isPluggedIn, isCharging, isOperating, isRunning
    
    pattern = re.compile(r'\s+')
    data = re.sub(pattern, '', data)
    
    if (msg_id == "477"):
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_operating = battery_current * battery_voltage / 1000.0

        soc = int(data[8] + data[9], 16)/2

        high_cell_voltage = int(data[12] + data[13] + data[10] + data[11], 16) * 0.0001
        high_cell_voltage_id = int(data[14] + data[15], 16)
        
        isOperating = 1  

    elif (msg_id == "478"):     # same as 477 but on charge
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_charging = battery_current * battery_voltage / 1000.0

        soc = int(data[8] + data[9], 16)/2.0

        high_cell_voltage = int(data[12] + data[13] + data[10] + data[11], 16) * 0.0001
        high_cell_voltage_id = int(data[14] + data[15], 16)
		
	isPluggedIn = 1
        if (battery_current) < -0.1:
            isCharging = 1

    elif (msg_id == "479" or msg_id == "480"):     # these two transmit the same info
        batt_high_temp = int(data[0] + data[1], 16)
        batt_high_temp = twos_comp(batt_high_temp, 8)
        
        batt_low_temp = int(data[2] + data[3], 16)
        batt_low_temp = twos_comp(batt_low_temp, 8)
        
        batt_high_temp_id = int(data[4] + data[5], 16)
        batt_low_temp_id = int(data[6] + data[7], 16)
        
        low_cell_voltage = int(data[10] + data[11] + data[8] + data[9], 16) * 0.0001
        low_cell_voltage_id = int(data[12] + data[13], 16)

    elif (msg_id == "475"):
        mc_cap_voltage = int(data[2] + data[3] + data[0] + data[1], 16)/16.0
        
        heatsink_temp = int(data[4] + data[5], 16)
        heatsink_temp = twos_comp(heatsink_temp, 8)
        
        active_fault = int(data[8] + data[9] + data[6] + data[7], 16)
        traction_state = int(data[10] + data[11], 16)
        motor_current = int(data[14] + data[15] + data[12] + data[13], 16)

    elif (msg_id == "270"):
        motor_voltage = int(data[14] + data[15] + data[12] + data[13], 16)/16.0

    elif (msg_id == "294"):
        CCL = int(data[6] + data[7] + data[4] + data[5], 16)
        CCL = twos_comp(CCL, 16)
        DCL = int(data[10] + data[11] + data[8] + data[9], 16)
        mc_battery_current = int(data[14] + data[15] + data[12] + data[13], 16)
        mc_battery_current = twos_comp(mc_battery_current, 16)/16.0

    elif (msg_id == "306"):
        motor_temp = int(data[2] + data[3] + data[0] + data[1], 16)
        motor_temp = twos_comp(motor_temp, 16)
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

    if (isCharging):
        battery_power_operating = 0 #don't show current in operating, it's going to be in charging

#connect to databases
logsDB=sqlite3.connect(logsPath)
logsCurs=logsDB.cursor()

while (True): #Checks the date, starts logging, when the logging ends (end of day, or end of time-period) it will transfer data to permanent location.
            
    #get x messages
    p = subprocess.Popen("candump -t A -n 10 can0,477:7ff,478:7ff,479:7ff,480:7ff,475:7ff,270:7ff,294:7ff,306:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    lines = output.strip().split("\n")
    
    #parse messages
    for line in lines:
        try:
            data = line.strip().split("  ")
            parse_data(data[2], data[4].strip()) #message id, message data
        except:
            print "Error parsing line: " + line
            pass

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
        
    #if over a second
    if time_span >= 1:

        #write values to dailyLogs database
        command = "INSERT INTO dailyLogs values('"

        command += current_date[0:10] + "','"
        command += current_date[11:19] + "','"
        command += str(soc) + "','"
        command += str(battery_current) + "','"
        command += str(battery_voltage) + "','"
        
        command += str(battery_power_operating) + "','"
        command += str(battery_power_charging) + "','"
        
        command += str(motor_current) + "','"
        command += str(motor_voltage) + "','"
        
        command += str(mc_battery_current) + "','"
        command += str(mc_cap_voltage) + "','"
        
        command += str(vehicle_speed) + "','"
        command += str(motor_velocity) + "','"
        
        command += str(active_fault) + "','"
        command += str(traction_state) + "','"
        
        command += str(DCL) + "','"
        command += str(CCL) + "','"
        
        command += str(motor_temp) + "','"
        command += str(heatsink_temp) + "','"
        
        command += str(batt_high_temp) + "','"
        command += str(batt_high_temp_id) + "','"
        command += str(batt_low_temp) + "','"
        command += str(batt_low_temp_id) + "','"
        
        command += str(high_cell_voltage) + "','"
        command += str(high_cell_voltage_id) + "','"
        command += str(low_cell_voltage) + "','"
        command += str(low_cell_voltage_id) + "','"
        
        command += str(isPluggedIn) + "','"
        command += str(isCharging) + "','"
        command += str(isOperating) + "','"
        command += str(isRunning)
    
        command += "');"

        logsCurs.execute(command)

        command = "INSERT OR IGNORE INTO days values('"
        command += current_date[0:10]
        command += "');"

        logsCurs.execute(command)
        logsDB.commit()

        #integrate certain variables over time to gets sums
        odometer = (abs(vehicle_speed) * time_span)/3600.0
        hours_plugged_in = (isPluggedIn * time_span)/3600.0
        hours_charging = (isCharging * time_span)/3600.0
        hours_operating = (isOperating * time_span)/3600.0
        hours_running = (isRunning  * time_span)/3600.0
        battery_energy_operating = (battery_power_operating * time_span)/3600.0
        battery_energy_charging = (battery_power_charging * time_span)/3600.0

        #retrieve old summary data if it exists
        logsCurs.execute("SELECT * FROM summary WHERE date='" + current_date[0:10] + "' LIMIT 1;")
        oldSummaryData = logsCurs.fetchall()

        if len(oldSummaryData) > 0:
            for datum in oldSummaryData:
                odometer += float(oldSummaryData[0][1])
                battery_energy_operating += float(oldSummaryData[0][2])
                battery_energy_charging += float(oldSummaryData[0][3])
                hours_plugged_in += float(oldSummaryData[0][4])
                hours_charging += float(oldSummaryData[0][5])
                hours_operating += float(oldSummaryData[0][6])
                hours_running += float(oldSummaryData[0][7])

            #update summary data in database
            command = "UPDATE summary SET odometer="
            command += str(odometer) + ",energy_out="
            command += str(battery_energy_operating) + ",energy_in="
            command += str(battery_energy_charging) + ",hours_plugged_in="
            command += str(hours_plugged_in) + ",hours_charging="
            command += str(hours_charging) + ",hours_operating="
            command += str(hours_operating) + ",hours_running="
            command += str(hours_running)
            command += " WHERE date='" + current_date[0:10] + "';" 
            
        else:
            #insert summary data into database
            command = "INSERT INTO summary VALUES('"
            command += current_date[0:10] + "','"
            command += str(odometer) + "','"
            command += str(battery_energy_operating) + "','"
            command += str(battery_energy_charging) + "','"
            command += str(hours_plugged_in) + "','"
            command += str(hours_charging) + "','"
            command += str(hours_operating) + "','"
            command += str(hours_running)
            command += "');"

        logsCurs.execute(command)
        logsDB.commit()

        #zero all data
        battery_current = battery_voltage = battery_power_operating = battery_power_charging = motor_current = 0
        motor_voltage = mc_cap_voltage = active_fault = traction_state = vehicle_speed = motor_velocity = soc = 0
        DCL = CCL = motor_temp = heatsink_temp = batt_high_temp = batt_high_temp_id = 0
        batt_low_temp = batt_low_temp_id = isPluggedIn = isCharging = isOperating = isRunning = 0
        high_cell_voltage = low_cell_voltage = high_cell_voltage_id = low_cell_voltage_id = 0
        odometer = battery_energy_operating = battery_energy_charging = hours_plugged_in = hours_charging = hours_operating = hours_running = 0
        high_cell_voltage = low_cell_voltage = high_cell_voltage_id = low_cell_voltage_id = 0
        
#close databases
logsDB.close()
