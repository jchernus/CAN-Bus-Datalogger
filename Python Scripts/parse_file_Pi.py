#!/usr/bin/python

import os, sys
from time import localtime, strftime

battery_current = battery_voltage = battery_power_in = battery_power_out = mc_cap_voltage = motor_current = 0
motor_voltage = mc_battery_current = vehicle_speed = motor_velocity = 0
soc = time_charging = vehicle_on_time = run_hours = 0
_soc = _time_charging = _vehicle_on_time = _run_hours = 0

odometer = hours_charging = hours_operating = hours_running = battery_energy = motor_energy = aux_energy = 0

last_time_stamp = thirty_second_time_stamp = None

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
    global battery_current, battery_voltage, battery_power_in, battery_power_out, mc_cap_voltage, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp, thirty_second_time_stamp, odometer, hours_charging, hours_operating, hours_running, battery_energy, motor_energy, aux_energy
    global soc, time_charging, vehicle_on_time, run_hours
    global _soc, _time_charging, _vehicle_on_time, _run_hours

    if (msg_id == "477"):
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_out = battery_current * battery_voltage
        battery_power_in = 0
        if (battery_power_out < 0):                                          #Negative designates charging or operating
            battery_power_in = -1 * battery_power_out
            battery_power_out = 0

        _soc = int(data[10] + data[11] + data[8] + data[9], 16)/2
        
        data_6 = str(bin(int(data[12] + data[13], 16)))[2:]
        while (len(data_6) < 8):
            data_6 = '0' + data_6
        _time_charging = int(data_6[3])
        _vehicle_on_time = int(data_6[4])

    elif (msg_id == "478"):     # same at 477 but on charge
        battery_current = int(data[2] + data[3] + data[0] + data[1], 16)
        battery_current = twos_comp(battery_current, 16)
        battery_current /= 10.0
        
        battery_voltage = int(data[6] + data[7] + data[4] + data[5], 16)/100.0
        battery_power_out = battery_current * battery_voltage
        battery_power_in = 0
        if (battery_power_out < 0):                                          #Negative designates charging or operating
            battery_power_in = -1 * battery_power_out
            battery_power_out = 0

        _soc = int(data[10] + data[11] + data[8] + data[9], 16)/2
        
        data_6 = str(bin(int(data[12] + data[13], 16)))[2:]
        while (len(data_6) < 8):
            data_6 = '0' + data_6
        _time_charging = int(data_6[3])
        _vehicle_on_time = int(data_6[4])
        
    elif (msg_id == "475"):
        mc_cap_voltage = int(data[2] + data[3] + data[0] + data[1], 16)/16.0
        motor_current = int(data[14] + data[15] + data[12] + data[13], 16)
        if (int(data[10] + data[11], 16) > 0):
            _run_hours = 1

    elif (msg_id == "270"):
        motor_voltage = int(data[14] + data[15] + data[12] + data[13], 16)

    elif (msg_id == "294"):
        mc_battery_current = int(data[14] + data[15] + data[12] + data[13], 16) * 0.0625
        mc_battery_current = twos_comp(mc_battery_current, 16)

    elif (msg_id == "306"):
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
        vehicle_speed = float(str(int(str_vs[0:-4],2)) + '.' + str(int(str_vs[-4:],2))) #Convert to 12.4 format.
        if isNegative:
            vehicle_speed *= -1
        motor_velocity = int(data[14] + data[15] + data[12] + data[13] + data[10] + data[11] + data[8] + data[9], 16) #Something special needs to be done with this
        motor_velocity = twos_comp(motor_velocity, 32)
    
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

    if time_span >= 1: #only care if two seconds have passed (first one is accounted for by last log)
        
        #convert variables from byte-strings to ints/floats        
        motor_power = motor_current * motor_voltage
        aux_power = battery_power_out - motor_power
    
        #integrate certain variables to gets sums
        odometer += (vehicle_speed * time_span)/3600.0
        hours_charging += (time_charging * time_span)/3600.0
        hours_operating += (vehicle_on_time * time_span)/3600.0
        hours_running += (run_hours  * time_span)/3600.0
        battery_energy += (battery_power_in * time_span)/3600.0
        motor_energy += (motor_power * time_span)/3600.0
        #aux_energy += (aux_power * time_span)/3600.0

        soc += _soc
        time_charging += _time_charging
        vehicle_on_time += _vehicle_on_time
        run_hours += _run_hours

        #write values to excel
        excelFile.write(current_time + ",")                                 #Time Stamp
        excelFile.write(str(battery_current) + ",")                         #Battery Current
        excelFile.write(str(battery_voltage) + ",")                         #Battery Voltage
        excelFile.write(str(battery_power_in) + ",")                        #Battery Power In
        excelFile.write(str(battery_power_out) + ",")                       #Battery Power Out
        excelFile.write(str(motor_current) + ",")                           #Motor Current
        excelFile.write(str(motor_voltage) + ",")                           #Motor Voltage
        excelFile.write(str(motor_power) + ",")                             #Motor Power
        excelFile.write(str(aux_power) + ",")                               #Auxiliary Power
        excelFile.write(str(mc_battery_current) + ",")                      #Motor Controller Battery Current
        excelFile.write(str(mc_cap_voltage) + ",")                          #Motor Controller Capacitor Voltage
        excelFile.write(str(vehicle_speed) + ",")                           #Vehicle Speed
        excelFile.write(str(motor_velocity) + ",")                          #Motor Velocity

        if thirty_second_time_stamp == None or (current_time_stamp - thirty_second_time_stamp) >= 30:

            if thirty_second_time_stamp is not None:
                soc = soc/30.0
                time_charging = time_charging/30.0
                vehicle_on_time = vehicle_on_time/30.0
                run_hours = run_hours/30.0
                
            excelFile.write(str(soc) + ",")                            #State Of Charge
            excelFile.write(str(time_charging) + ",")                  #Time Charging
            excelFile.write(str(vehicle_on_time) + ",")                #Vehicle On Time
            excelFile.write(str(run_hours) + ",")                      #Vehicle Run Hours
            
            soc = time_charging = vehicle_on_time = run_hours = 0
            
            thirty_second_time_stamp = current_time_stamp
            
        excelFile.write("\n")

##cmdargs = []
##for file in os.listdir("\data\scripts\Datalogs"):
##    if file.endswith(".log"):
##        cmdargs.append("\data\scripts\Datalogs\\" + file)

cmdargs = sys.argv[1:]

for file in cmdargs:
    with open(path + file, 'r+') as f: #open files as read only

        #create & start the excel file that will house the parsed data
        fileName = file[:6] + "dailylogs" + file[9:10] + file[18:len(file)-11] + ".csv" #strip off the two digits for hours and the ".log"      #/data/RAW/candump-2015-02-16_113546.log
        file_existed = False
        if os.path.exists(fileName):
            file_existed = True
            
        if file_existed: #read in existing values
            with open(fileName, 'r+') as parsedFile:
                line = parsedFile.readline() #ignore the first line
                line = parsedFile.readline() #we want this second line
                sums = line.strip().split(",")

                odometer = float(sums[1])
                battery_energy = float(sums[2])
                motor_energy = float(sums[3])
                aux_energy = float(sums[4])
                hours_charging = float(sums[5])
                hours_running = float(sums[6])
                hours_operating = float(sums[7])
                
        excelFile = open(path + fileName, 'a+')
        if not file_existed: #the file was just created, add the top column headings
            excelFile.write('\n                                                                                                                                                                                                                     ')
            excelFile.write('\n                                                                                                                                                                                                                                           ')
            excelFile.write('\nTime Stamp, Battery Current, Battery Voltage, Battery Power In, Battery Power Out, Motor Current (AC), Motor Voltage (AC), Motor Power, Auxiliary Power, Motor Controller Battery Current, Motor Controller Capacitor Voltage, Vehicle Speed, Motor Velocity (RPM), SOC, Time Charging, Time Operating, Vehicle Run Hours \n')

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
    excelFile.write('Date, Odometer, Battery Energy, Motor Energy, Auxiliary Energy, Hours Charging, Hours Running, Hours On\n')
    excelFile.write(fileName[31:-4] +  ',' + str(odometer) +  ',' + str(battery_energy) +  ',' + str(motor_energy) +  ',' + str(aux_energy) +  ',' + str(hours_charging) +  ',' + str(hours_running) +  ',' + str(hours_operating))
    excelFile.close()
