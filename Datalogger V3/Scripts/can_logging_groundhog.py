#!/usr/bin/env python

import subprocess, os, re, sqlite3

battery_current = battery_voltage = battery_power_operating = battery_power_charging = soc = 0
battery_current1 = battery_voltage1 = mc_cap_voltage1 = heatsink_temp1 = motor_temp1 = motor_current1 = motor_velocity1 = torque1 = target_torque1 = active_fault1 = 0
battery_current2 = battery_voltage2 = mc_cap_voltage2 = heatsink_temp2 = motor_temp2 = motor_current2 = motor_velocity2 = torque2 = target_torque2 = active_fault2 = 0
battery_current3 = battery_voltage3 = mc_cap_voltage3 = heatsink_temp3 = motor_temp3 = motor_current3 = motor_velocity3 = torque3 = target_torque3 = active_fault3 = 0
status_word1 = status_word2 = status_word3 = ""
DCL = CCL = batt_high_temp = batt_low_temp = batt_high_temp_id = batt_low_temp_id = 0
high_cell_voltage = low_cell_voltage = high_cell_voltage_id = low_cell_voltage_id = 0
isPluggedIn = isCharging = isOperating = isRunning = 0

odometer = hours_plugged_in = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = motor_energy = aux_energy = 0

previous_time = 0

logsPath = "/data/databases/GroundHogLogs.db"

def twos_comp(val, bits):
    #compute the 2's compliment of int value val
    val = int(val)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

def parse_data(msg_id, data):
    global battery_current, battery_voltage, battery_power_operating, battery_power_charging, soc
    global battery_current1, battery_voltage1, mc_cap_voltage1, heatsink_temp1, motor_temp1, motor_current1, motor_velocity1, torque1, target_torque1, active_fault1, status_word1
    global battery_current2, battery_voltage2, mc_cap_voltage2, heatsink_temp2, motor_temp2, motor_current2, motor_velocity2, torque2, target_torque2, active_fault2, status_word2
    global battery_current3, battery_voltage3, mc_cap_voltage3, heatsink_temp3, motor_temp3, motor_current3, motor_velocity3, torque3, target_torque3, active_fault3, status_word3
    global last_time_stamp, odometer, hours_plugged_in, hours_charging, hours_operating, hours_running, battery_energy_operating, battery_energy_charging
    global DCL, CCL, batt_high_temp, batt_low_temp, batt_high_temp_id, batt_low_temp_id
    global high_cell_voltage, low_cell_voltage, high_cell_voltage_id, low_cell_voltage_id
    global isPluggedIn, isCharging, isOperating, isRunning
    
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

    elif (msg_id == "201"):
        status_word1 = str(data[2] + data[3] + data[0] + data[1])
        mc_cap_voltage1 = int(data[6] + data[7] + data[4] + data[5], 16)/16.0
        battery_voltage1 = int(data[10] + data[11] + data[8] + data[9], 16)/16.0

    elif (msg_id == "202"):
        status_word2 = str(data[2] + data[3] + data[0] + data[1])
        mc_cap_voltage2 = int(data[6] + data[7] + data[4] + data[5], 16)/16.0
        battery_voltage2 = int(data[10] + data[11] + data[8] + data[9], 16)/16.0

    elif (msg_id == "203"):
        status_word3 = str(data[2] + data[3] + data[0] + data[1])
        mc_cap_voltage3 = int(data[6] + data[7] + data[4] + data[5], 16)/16.0
        battery_voltage3 = int(data[10] + data[11] + data[8] + data[9], 16)/16.0	

    elif (msg_id == "301"):
        motor_velocity1 = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16)
        motor_velocity1 = twos_comp(motor_velocity1, 32)

        motor_temp1 = int(data[10] + data[11] + data[8] + data[9], 16)
        motor_temp1 = twos_comp(motor_temp1, 16)

    elif (msg_id == "302"):
        motor_velocity2 = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16)
        motor_velocity2 = twos_comp(motor_velocity2, 32)

        motor_temp2 = int(data[10] + data[11] + data[8] + data[9], 16)
        motor_temp2 = twos_comp(motor_temp2, 16)

    elif (msg_id == "303"):
        motor_velocity3 = int(data[6] + data[7] + data[4] + data[5] + data[2] + data[3] + data[0] + data[1], 16)
        motor_velocity3 = twos_comp(motor_velocity3, 32)

        motor_temp3 = int(data[10] + data[11] + data[8] + data[9], 16)
        motor_temp3 = twos_comp(motor_temp3, 16)

    elif (msg_id == "391"):
        battery_current1 = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current1 = twos_comp(battery_current1, 16)
        battery_current1 /= 10.0

        motor_current1 = int(data[6] + data[7] + data[4] + data[5], 16)

        torque1 = int(data[10] + data[11] + data[8] + data[9], 16)
        torque1 = twos_comp(torque1, 16)

        heatsink_temp1 = int(data[12] + data[13], 16)
        heatsink_temp1 = twos_comp(heatsink_temp1, 8)

    elif (msg_id == "392"):
        battery_current2 = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current2 = twos_comp(battery_current2, 16)
        battery_current2 /= 10.0

        motor_current2 = int(data[6] + data[7] + data[4] + data[5], 16)

        torque2 = int(data[10] + data[11] + data[8] + data[9], 16)
        torque2 = twos_comp(torque2, 16)

        heatsink_temp2 = int(data[12] + data[13], 16)
        heatsink_temp2 = twos_comp(heatsink_temp2, 8)

    elif (msg_id == "393"):
        battery_current3 = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current3 = twos_comp(battery_current3, 16)
        battery_current3 /= 10.0

        motor_current3 = int(data[6] + data[7] + data[4] + data[5], 16)

        torque3 = int(data[10] + data[11] + data[8] + data[9], 16)
        torque3 = twos_comp(torque3, 16)

        heatsink_temp3 = int(data[12] + data[13], 16)
        heatsink_temp3 = twos_comp(heatsink_temp3, 8)  

    elif (msg_id == "397"):
        target_torque1 = int(data[10] + data[11] + data[8] + data[9], 16)
        target_torque1 = twos_comp(target_torque1, 16)
        active_fault1 = int(data[14] + data[15] + data[12] + data[13], 16)  

    elif (msg_id == "398"):
        target_torque2 = int(data[10] + data[11] + data[8] + data[9], 16)
        target_torque2 = twos_comp(target_torque2, 16)
        active_fault2 = int(data[14] + data[15] + data[12] + data[13], 16)  

    elif (msg_id == "399"):
        target_torque3 = int(data[10] + data[11] + data[8] + data[9], 16)
        target_torque3 = twos_comp(target_torque3, 16)
        active_fault3 = int(data[14] + data[15] + data[12] + data[13], 16)

    elif (msg_id == "3FF"):
        CCL = int(data[2] + data[3] + data[0] + data[1], 16)
        CCL = twos_comp(CCL, 16)
        DCL = int(data[6] + data[7] + data[4] + data[5], 16)

#connect to databases
logsDB=sqlite3.connect(logsPath)
logsCurs=logsDB.cursor()

while (True): #Checks the date, starts logging, when the logging ends (end of day, or end of time-period) it will transfer data to permanent location.
            
    #get x messages
    p = subprocess.Popen("candump -t A -n 12 can0,201:7ff,202:7ff,203:7ff,301:7ff,302:7ff,303:7ff,391:7ff,392:7ff,393:7ff,397:7ff,398:7ff,399:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    lines = output.strip().split("\n")

    p = subprocess.Popen("candump -t A -n 4 can0,477:7ff,478:7ff,479:7ff,3ff:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    lines = lines + output.strip().split("\n")
    
    #parse messages
    for line in lines:
        try:
            data = line.strip().split("  ")
            parse_data(data[2], data[4].strip()) #message id, message data
        except:
            print "Error parsing line: " + line
            pass

    #do some post-processing
    if (isCharging):
        battery_power_operating = 0 #don't show current in operating, it's going to be in charging

    if motor_velocity1 <= -1 or motor_velocity1 >= 1 or motor_velocity2 <= -1 or motor_velocity2 >= 1 or motor_velocity3 <= -1 or motor_velocity3 >= 1:
        isRunning = 1
    else:
        isRunning = 0

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

        #calculate vehicle speed
        vehicle_speed = motor_velocity1/180.0

        #write values to dailyLogs database
        command = "INSERT INTO dailyLogs values('"

        command += current_date[0:10] + "','"
        command += current_date[11:19] + "','"
        
        command += str(soc) + "','"
        command += str(battery_current) + "','"
        command += str(battery_voltage) + "','"
        command += str(battery_power_operating) + "','"
        command += str(battery_power_charging) + "','"
        command += str(vehicle_speed) + "','"
        
        command += str(battery_current1) + "','"
        command += str(battery_voltage1) + "','"
        command += str(mc_cap_voltage1) + "','"
        command += str(motor_current1) + "','"
        command += str(motor_velocity1) + "','"
        command += str(torque1) + "','"
        command += str(target_torque1) + "','"
        command += str(active_fault1) + "','"
        command += str(heatsink_temp1) + "','"
        command += str(motor_temp1) + "','"
        command += str(status_word1) + "','"

        command += str(battery_current2) + "','"
        command += str(battery_voltage2) + "','"
        command += str(mc_cap_voltage2) + "','"
        command += str(motor_current2) + "','"
        command += str(motor_velocity2) + "','"
        command += str(torque2) + "','"
        command += str(target_torque2) + "','"
        command += str(active_fault2) + "','"
        command += str(heatsink_temp2) + "','"
        command += str(motor_temp2) + "','"
        command += str(status_word2) + "','"
        
        command += str(battery_current3) + "','"
        command += str(battery_voltage3) + "','"
        command += str(mc_cap_voltage3) + "','"
        command += str(motor_current3) + "','"
        command += str(motor_velocity3) + "','"
        command += str(torque3) + "','"
        command += str(target_torque3) + "','"
        command += str(active_fault3) + "','"
        command += str(heatsink_temp3) + "','"
        command += str(motor_temp3) + "','"
        command += str(status_word3) + "','"

        
        command += str(DCL) + "','"
        command += str(CCL) + "','"
        
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
        battery_current = battery_voltage = battery_power_operating = battery_power_charging = soc = 0
        battery_current1 = battery_voltage1 = mc_cap_voltage1 = heatsink_temp1 = motor_temp1 = motor_current1 = motor_velocity1 = torque1 = target_torque1 = active_fault1 = 0
        battery_current2 = battery_voltage2 = mc_cap_voltage2 = heatsink_temp2 = motor_temp2 = motor_current2 = motor_velocity2 = torque2 = target_torque2 = active_fault2 = 0
        battery_current3 = battery_voltage3 = mc_cap_voltage3 = heatsink_temp3 = motor_temp3 = motor_current3 = motor_velocity3 = torque3 = target_torque3 = active_fault3 = 0
        status_word1 = status_word2 = status_word3 = ""
        DCL = CCL = batt_high_temp = batt_low_temp = batt_high_temp_id = batt_low_temp_id = 0
        isPluggedIn = isCharging = isOperating = isRunning = 0

        odometer = hours_plugged_in = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = motor_energy = aux_energy = 0
        
#close databases
logsDB.close()
