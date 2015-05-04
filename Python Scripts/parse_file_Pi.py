#!/usr/bin/python

import os, sys
from time import localtime, strftime

battery_current = battery_voltage = battery_power_operating = battery_power_charging = 0
mc_cap_voltage = heatsink_temp = current_fault = traction_state = motor_temp = motor_current = 0
motor_voltage = mc_battery_current = vehicle_speed = motor_velocity = max_batt_discharge_current = max_batt_charge_current = 0
soc = isCharging = isOperating = isRunning = 0
batt_high_temp = batt_low_temp = batt_high_temp_id = batt_low_temp_id = 0

odometer = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = motor_energy = aux_energy = 0

last_time_stamp = None

path = ""

#create the paths that are needed to store files
if (not os.path.exists("/data/dailylogs")):
    os.mkdir("/data/dailylogs")

def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    val = int(val)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

def parse_data(time_stamp, msg_id, data):
    global battery_current, battery_voltage, battery_power_operating, battery_power_charging
    global mc_cap_voltage, heatsink_temp, current_fault, traction_state, motor_temp, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp, odometer, hours_charging, hours_operating, hours_running, battery_energy_operating, battery_energy_charging
    global max_batt_discharge_current, max_batt_charge_current
    global soc, isCharging, isOperating, isRunning
    global batt_high_temp, batt_low_temp, batt_high_temp_id, batt_low_temp_id

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
##        isCharging = int(data_6[3])
##        isOperating = int(data_6[4])
        isOperating = 1  

    elif (msg_id == "478"):     # same as 477 but on charge
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_charging = battery_current * battery_voltage / 1000.0

        soc = int(data[10] + data[11] + data[8] + data[9], 16)/2
        
        data_6 = str(bin(int(data[12] + data[13], 16)))[2:]
        while (len(data_6) < 8):
            data_6 = '0' + data_6
##        isCharging = int(data_6[4])
##        isOperating = int(data_6[3])
        isCharging = 1

    elif (msg_id == "479" or msg_id == "480"):     # the two transmit the same info
        batt_high_temp = int(data[0] + data[1], 16)
        batt_low_temp = int(data[4] + data[5], 16)
        batt_high_temp_id = int(data[8] + data[9], 16)
        batt_low_temp_id = int(data[10] + data[11], 16)

    elif (msg_id == "475"):
        mc_cap_voltage = int(data[2] + data[3] + data[0] + data[1], 16)/16.0
        heatsink_temp = int(data[4] + data[5], 16)
        current_fault = int(data[8] + data[9] + data[6] + data[7], 16)
        traction_state = int(data[10] + data[11], 16)
        motor_current = int(data[14] + data[15] + data[12] + data[13], 16)
##        if (int(data[10] + data[11], 16) > 0):
##            isRunning = 1

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
    
    #calculate time difference between current and previous time stamps
    current_time = strftime('%H:%M:%S', localtime(time_stamp))
    times = str(current_time).split(":")
    current_time_stamp = int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2]) #convert to seconds
    time_span = 1 #if there is no previous time stamp, assume 1s
    if last_time_stamp is not None:
        time_span = (current_time_stamp - last_time_stamp)
        if time_span > 2: #if time between time stamps is too long, assume 1s
            time_span = 1
    last_time_stamp = current_time_stamp

    if time_span >= 1:
    
        #integrate certain variables to gets sums
        odometer += (abs(vehicle_speed) * time_span)/3600.0
        hours_charging += (isCharging * time_span)/3600.0
        hours_operating += (isOperating * time_span)/3600.0
        hours_running += (isRunning  * time_span)/3600.0
        battery_energy_operating += (battery_power_operating * time_span)/3600.0
        battery_energy_charging += (battery_power_charging * time_span)/3600.0

        #write values to excel
        excelFile.write(current_time + ",")                                 #Time Stamp
               
        excelFile.write(str(soc) + ",")                                     #State Of Charge
        
        excelFile.write(str(battery_current) + ",")                         #Battery Current
        excelFile.write(str(battery_voltage) + ",")                         #Battery Voltage
        excelFile.write(str(battery_power_operating) + ",")                 #Battery Power Operating
        excelFile.write(str(battery_power_charging) + ",")                  #Battery Power Charging
        
        excelFile.write(str(motor_current) + ",")                           #Motor Current AC RMS
        excelFile.write(str(motor_voltage) + ",")                           #Motor Voltage AC RMS
        
##        excelFile.write(str(mc_battery_current) + ",")                      #Motor Controller Battery Current
        excelFile.write(str(mc_cap_voltage) + ",")                          #Motor Controller Capacitor Voltage

        excelFile.write(str(vehicle_speed) + ",")                           #Vehicle Speed
        excelFile.write(str(motor_velocity) + ",")                          #Motor Velocity

        excelFile.write(str(current_fault) + ",")                           #Current Highest Priority Fault
        excelFile.write(str(traction_state) + ",")                          #Traction State

        excelFile.write(str(max_batt_discharge_current) + ",")              #Maximum Battery Discharge Current
        excelFile.write(str(max_batt_charge_current) + ",")                 #Maximum Battery Charge Current

        excelFile.write(str(motor_temp) + ",")                              #Motor Temperature        
        excelFile.write(str(heatsink_temp) + ",")                           #Motor Controller Heatsink Temperature

        excelFile.write(str(batt_high_temp) + ",")                          #Battery High Temp
        excelFile.write(str(batt_high_temp_id) + ",")                       #Battery High Temp ID

        excelFile.write(str(batt_low_temp) + ",")                           #Battery Low Temp     
        excelFile.write(str(batt_low_temp_id) + ",")                        #Battery Low Temp ID
        
        excelFile.write(str(isCharging) + ",")                              #Time Charging
        excelFile.write(str(isOperating) + ",")                             #Vehicle On Time
        excelFile.write(str(isRunning) + ",")                               #Vehicle Run Hours
            
        excelFile.write("\n")

        #reset them all to 0
        battery_current = battery_voltage = battery_power_operating = battery_power_charging = motor_current = 0
        motor_voltage = mc_cap_voltage = current_fault = traction_state = vehicle_speed = motor_velocity = soc = 0
        max_batt_discharge_current = max_batt_charge_current = motor_temp = heatsink_temp = batt_high_temp = batt_high_temp_id = 0
        batt_low_temp = batt_low_temp_id = isCharging = isOperating = isRunning = 0

##cmdargs = []
##for file in os.listdir("\data\scripts\Datalogs"):
##    if file.endswith(".log"):
##        cmdargs.append("\data\scripts\Datalogs\\" + file)

cmdargs = sys.argv[1:]

for file in cmdargs:
    with open(path + file, 'r+') as f: #open files as read only

        #create & start the excel file that will house the parsed data
        fileName = file[:6] + "dailylogs" + file[9:10] + "_" + file[18:len(file)-11] + ".csv" #strip off the two digits for hours and the ".log"      #/data/RAW/candump-2015-02-16_113546.log
        file_existed = False
        if os.path.exists(fileName):
            file_existed = True
            
        if file_existed: #read in existing values
            try:
                with open(fileName, 'r+') as parsedFile:
                    line = parsedFile.readline() #ignore the first line
                    line = parsedFile.readline() #we want this second line
                    sums = line.strip().split(",")

                    odometer = float(sums[1])
                    battery_energy_operating = float(sums[2])
                    battery_energy_charging = float(sums[3])
                    hours_charging = float(sums[4])
                    hours_operating = float(sums[5])
                    hours_running = float(sums[6])
                        
            except (ValueError, IndexError): #variables garbled, can't convert into floats
                try: 
                    os.rename(fileName, fileName[:-15] + "Error" + fileName[-15:])
                except: # may already exist, just delete the older one then
                    os.remove(fileName[:-15] + "Error" + fileName[-15:])
                    os.rename(fileName, fileName[:-15] + "Error" + fileName[-15:])
                file_existed = False
                
        excelFile = open(path + fileName, 'a+')
        if not file_existed: #the file was just created, add the top column headings
            excelFile.write('\n                                                                                                                                                                                                                          ')
            excelFile.write('\n                                                                                                                                                                                                                                                ')
            excelFile.write('\n\nTime Stamp, SOC [%], Battery Current [A], Battery Voltage [V], Battery Power Out (Operating) [kW], Battery Power In (Charging)[kW], Motor Current [AC A rms], Motor Voltage [AC V rms], Motor Controller Capacitor Voltage [V], Vehicle Speed [km/h], Motor Velocity [RPM], Current Highest Priority Fault, Traction State, Maximum Battery Discharge Current [A], Maximum Battery Charge Current [A], Motor Temperature [Celcius], Motor Controller Heatsink Temperature [Celcius], Battery Pack Highest Temperature [Celcius], Batt High Temp ID, Batter Pack Lowest Temperature [Celcius], Batt Low Temp ID, Charging, Operating, Running\n')

        for line in f:
            data = line.strip().split(" ")
            try:
                msg = data[2].strip().split("#")
                parse_data(float(data[0][1:-1]), msg[0], msg[1]) #time stamp, message id, message
            except IndexError:
                pass

    #Write summations to first and second lines in the .csv file.
    excelFile = open(path + fileName, 'r+')
    excelFile.seek(0)
    excelFile.write('Date, Odometer [km], Battery Energy Out (Operating) [kWh], Battery Energy In (Charging)[kWh], Hours Charging [h], Hours Operating [h], Hours Running [h]\n')

    #Convert all of the variables to strings and ensure they are at least 16 characters long each, this will prevent them from writing over the old date and causing "10.07.07"

    str_odometer = str(odometer)
    if (len(str_odometer) > 16):
        str_odometer = str_odometer[:16]
    while (len(str_odometer) < 16):
        str_odometer = '0' + str_odometer

    str_battery_energy_operating = str(battery_energy_operating)
    if (len(str_battery_energy_operating) > 16):
        str_battery_energy_operating = str_battery_energy_operating[:16]
    while (len(str_battery_energy_operating) < 16):
        str_battery_energy_operating = '0' + str_battery_energy_operating

    str_battery_energy_charging = str(battery_energy_charging)
    if (len(str_battery_energy_charging) > 16):
        str_battery_energy_charging = str_battery_energy_charging[:16]
    while (len(str_battery_energy_charging) < 16):
        str_battery_energy_charging = '0' + str_battery_energy_charging

    str_hours_charging = str(hours_charging)
    if (len(str_hours_charging) > 16):
        str_hours_charging = str_hours_charging[:16]
    while (len(str_hours_charging) < 16):
        str_hours_charging = '0' + str_hours_charging

    str_hours_operating = str(hours_operating)
    if (len(str_hours_operating) > 16):
        str_hours_operating = str_hours_operating[:16]
    while (len(str_hours_operating) < 16):
        str_hours_operating = '0' + str_hours_operating

    str_hours_running = str(hours_running)
    if (len(str_hours_running) > 16):
        str_hours_running = str_hours_running[:16]
    while (len(str_hours_running) < 16):
        str_hours_running = '0' + str_hours_running
    
    excelFile.write(fileName[17:-4] +  ',' + str_odometer +  ',' + str_battery_energy_operating +  ',' + str_battery_energy_charging +  ',' + str_hours_charging +  ',' + str_hours_operating +  ',' + str_hours_running)
    excelFile.close()
