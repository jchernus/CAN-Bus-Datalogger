import subprocess, os
from time import localtime, strftime

battery_current = battery_voltage = battery_power_operating = battery_power_charging = mc_cap_voltage = motor_current = 0
motor_voltage = mc_battery_current = vehicle_speed = motor_velocity = 0
soc = isCharging = isOperating = isRunning = 0

odometer = hours_charging = hours_operating = hours_running = battery_energy_operating = battery_energy_charging = motor_energy = aux_energy = 0

previous_date = "", previous_time = 0

path = ""

def twos_comp(val, bits):
    #compute the 2's compliment of int value val
    val = int(val)
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

def parse_data(time_stamp, msg_id, data):
    global battery_current, battery_voltage, battery_power_operating, battery_power_charging, mc_cap_voltage, motor_current, motor_voltage, mc_battery_current, vehicle_speed, motor_velocity
    global last_time_stamp, odometer, hours_charging, hours_operating, hours_running, battery_energy_operating, battery_energy_charging
    global soc, isCharging, isOperating, isRunning

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
        
    elif (msg_id == "475"):
##        mc_cap_voltage = int(data[2] + data[3] + data[0] + data[1], 16)/16.0
        motor_current = int(data[14] + data[15] + data[12] + data[13], 16)
##        if (int(data[10] + data[11], 16) > 0):
##            isRunning = 1

    elif (msg_id == "270"):
        motor_voltage = int(data[14] + data[15] + data[12] + data[13], 16) * 0.0625

##    elif (msg_id == "294"):
##        mc_battery_current = int(data[14] + data[15] + data[12] + data[13], 16)
##        mc_battery_current = twos_comp(mc_battery_current, 16)
##        mc_battery_current = mc_battery_current * 0.0625
##
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

        if vehicle_speed <= -0.1 or vehicle_speed >= 0.1:
            isRunning = 1
        else:
            isRunning = 0

#Create the paths that are needed to store files
if (not os.path.exists("/data/dailylogs")):
    os.mkdir("/data/dailylogs")

while (True):
    #Check the date
    p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    filename = output.strip() + ".csv"

    #Does a file for today's date already exist?
    if os.path.exists("/data/dailylogs/" + filename):
        #File exists, we need to read in existing data
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
                os.rename(fileName, fileName[0:-4] + "_Error" + ".csv")
            except: # may already exist, just delete the older one then
                os.remove(fileName[0:-4] + "_Error" + ".csv")
                os.rename(fileName, fileName[0:-4] + "_Error" + ".csv")
            file_existed = False

    else:
        #File does not exist, we need to create it
        if not file_existed:
            excelFile = open(path + fileName, 'w+')
            excelFile.write('\n                                                                                                                                                                                                                          ')
            excelFile.write('\n                                                                                                                                                                                                                                                ')
            excelFile.write('\n\nTime Stamp, Battery Current [A], Battery Voltage [V], Battery Power Out (Operating) [kW], Battery Power In (Charging)[kW], Motor Current [AC A rms], Motor Voltage [AC V rms], Vehicle Speed [km/h], Motor Velocity [RPM], SOC [%], Charging, Operating, Running\n')
            excelFile.close()

    while(True):
        
        #get x messages
        p = subprocess.Popen("candump -n<10> can0,477:7ff,478:7ff,475:7ff,270:7ff,294:7ff,306:7ff", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        lines = output.strip().split("\n")
        
        #parse messages
        for line in lines:
            data = line.strip().split(" ")
            msg = data[2].strip().split("#")
            parse_data(float(data[0][1:-1]), msg[0], msg[1]) #time stamp, message id, message

        #get date & time
        p = subprocess.Popen("date +\"%Y-%m-%d %H:%M:%S\"", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        current_date = output

        #if new date, break
        if (current_date[:10] != previous_date[:10]):
            break     #this will exit this while loop and return to the parent one, creating a new file (with the new date)
        
        #calculate time difference between current and previous time stamps
        times = str(current_date[11:19]).split(":")
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
            
            #write values to excel
            excelFile = open(path + fileName, 'a+')
            
            excelFile.write(current_time + ",")                                 #Time Stamp
            excelFile.write(str(battery_current) + ",")                         #Battery Current
            excelFile.write(str(battery_voltage) + ",")                         #Battery Voltage
            excelFile.write(str(battery_power_operating) + ",")                 #Battery Power Operating
            excelFile.write(str(battery_power_charging) + ",")                  #Battery Power Charging
            excelFile.write(str(motor_current) + ",")                           #Motor Current
            excelFile.write(str(motor_voltage) + ",")                           #Motor Voltage
##                excelFile.write(str(mc_battery_current) + ",")                      #Motor Controller Battery Current
##                excelFile.write(str(mc_cap_voltage) + ",")                          #Motor Controller Capacitor Voltage
            excelFile.write(str(vehicle_speed) + ",")                           #Vehicle Speed
            excelFile.write(str(motor_velocity) + ",")                          #Motor Velocity
                   
            excelFile.write(str(soc) + ",")                                     #State Of Charge
            excelFile.write(str(isCharging) + ",")                              #Time Charging
            excelFile.write(str(isOperating) + ",")                             #Vehicle On Time
            excelFile.write(str(isRunning) + ",")                               #Vehicle Run Hours
                
            excelFile.write("\n")
            excelFile.close()
    
            #integrate certain variables to gets sums
            odometer += (vehicle_speed * time_span)/3600.0
            hours_charging += (isCharging * time_span)/3600.0
            hours_operating += (isOperating * time_span)/3600.0
            hours_running += (isRunning  * time_span)/3600.0
            battery_energy_operating += (battery_power_operating * time_span)/3600.0
            battery_energy_charging += (battery_power_charging * time_span)/3600.0

            #Write summations to first and second lines in the .csv file.
            excelFile = open(path + fileName, 'r+')
            excelFile.seek(0)
            excelFile.write('Date, Odometer [km], Battery Energy Out (Operating) [kJ], Battery Energy In (Charging)[kJ], Hours Charging [h], Hours Operating [h], Hours Running [h]\n')
            excelFile.write(fileName[17:-4] +  ',' + str(odometer) +  ',' + str(battery_energy_operating) +  ',' + str(battery_energy_charging) +  ',' + str(hours_charging) +  ',' + str(hours_operating) +  ',' + str(hours_running))
            excelFile.close()
                
        #zero all data
        battery_current = battery_voltage = battery_power_operating = battery_power_charging = motor_current = 0
        motor_voltage = vehicle_speed = motor_velocity = soc = isCharging = isOperating = isRunning = 0

        #first run is just a trial, only run everything once.
        break
    break

