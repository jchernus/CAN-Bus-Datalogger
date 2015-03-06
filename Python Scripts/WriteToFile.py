import os, shutil

thirty_sec_counter = 0
odometer = hours_charging = hours_operating = hours_running = battery_energy = motor_energy = aux_energy = 0
soc = time_charging = vehicle_on_time = run_hours = 0
last_time_stamp = None

#confirm your original path
print("Path at terminal when executing this file")
print(os.getcwd() + "\n")

#create the paths that are needed to store files
if (not os.path.exists("Datalogs")):
    os.mkdir("Datalogs")
if (not os.path.exists("Datalogs/RAW")):
    os.mkdir("Datalogs/RAW")

def parse_date(date):
    year = "20" + date[0:2]
    day = str(int(date[5:7]))
    
    date = date[2:5].upper()
    month = "NUL"
    if date == "Jan":
        month = "January"
    elif date == "Feb":
        month[0] = 'F'
    elif date == "Mar":
        month = "March"
    elif date == "Apr":
        month = "April"
    elif date[0] == 'M':
        month = "May"
    elif date == "Jun":
        month = "June"
    elif date[0] == 'J':
        month == "July"
    elif date[0] == 'A':
        month == "August"
    elif date[0] == 'S':
        month == "September"
    elif date[0] == 'O':
        month == "October"
    elif date[0] == 'N':
        month == "November"
    elif date[0] == 'D':
        month = "December"

    full_date = month + " " + day + " " + year
    return full_date

def parse_data(fileName, data):
    global last_time_stamp, odometer, hours_charging, hours_operating, hours_running, battery_energy, motor_energy, aux_energy
    global soc, time_charging, vehicle_on_time, run_hours
    global thirty_sec_counter

    #convert variables from byte-strings to ints/floats
    battery_current = int(data[2] + data[1], 16)
    if (battery_current >= 32768):                                      #Signed 16bit
        battery_current = -1 * (battery_current - 32768)
    battery_current /= 10
    
    battery_voltage = int(data[4] + data[3], 16)/100
    battery_power_in = battery_current * battery_voltage
    battery_power_out = 0
    if (battery_power_in < 0):                                          #Negative designates charging or operating
        battery_power_out = -1 * battery_power_in
        battery_power_in = 0
        
    mc_cap_voltage = int(data[6] + data[5], 16)/16
    
    motor_current = int(data[8] + data[7], 16)
    motor_voltage = int(data[10] + data[9], 16)
    motor_power = motor_current * motor_voltage
    aux_power = battery_power_out - motor_power
    
    mc_battery_current = int(data[12] + data[11], 16)
    
    vehicle_speed = int(data[14] + data[13], 16)
    motor_velocity = int(data[18] + data[17] + data[16] + data[15], 16) #Something special needs to be done with this

    #these variables are rolling averages and only need to be saved every 30 seconds
    soc += int(data[20] + data[19], 16)/2

    data_21 = str(bin(int(data[21], 16)))[2:]
    while (len(data_21) < 16):
        data_21 = '0' + data_21

    time_charging += int(data_21[2])
    vehicle_on_time += int(data_21[3])

    if (int(data[22], 16) > 0):
        run_hours += 1

    thirty_sec_counter += 1

    #calculate time difference between current and previous time stamps
    times = data[0].split(":")
    current_time_stamp = int(times[0]) * 3600 + int(times[1] * 60) + int(times[2]) #convert to seconds
    time_span = 1/3600                                                  #if there is no previous time stamp, assume 1s
    if last_time_stamp is not None:
        time_span = (current_time_stamp - last_time_stamp)/3600.0
        if time_span > 2:                                               #if time between time stamps is too long, assume 1s
            time_span = 1/3600
    last_time_stamp = current_time_stamp

    #integrate certain variables to gets sums
    odometer += (vehicle_speed * time_span)
    hours_charging += (time_charging * time_span)
    hours_operating += (vehicle_on_time * time_span)
    hours_running += (run_hours  * time_span)
    battery_energy += (battery_power_in * time_span)
    motor_energy += (motor_power * time_span)
    aux_energy += (aux_power * time_span)

    #write values to excel
    excelFile.write(data[0] + ",")                                      #Time Stamp
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

    if (thirty_sec_counter >= 30):
        excelFile.write(str(soc/30) + ",")                              #State Of Charge
        excelFile.write(str(time_charging/30) + ",")                    #Time Charging
        excelFile.write(str(vehicle_on_time/30) + ",")                  #Vehicle On Time
        excelFile.write(str(run_hours/30) + ",")                        #Vehicle Run Hours

        soc = time_charging = vehicle_on_time = run_hours = 0
        thirty_sec_counter = 0
    excelFile.write("\n")


#process all of the files in the Datalogs directory that end in .txt
for file in os.listdir("Datalogs"):
    if file.endswith(".txt"):
        with open(file, 'r+') as f: #open files as read only

            #create & start the excel file that will house the parsed data
            fileName = file[:len(file)-4] + ".csv"
            excelFile = open(fileName, 'a+')
            excelFile.write('\n                                                                                                                                                                                                                     ')
            excelFile.write('\n                                                                                                                                                                                                                                           ')
            excelFile.write('\nTime Stamp, Battery Amperage, Battery Voltage, Battery Power In, Battery Power Out, Motor Current, Motor Voltage, Motor Power, Auxiliary Power, Motor Controller Battery Current, Motor Controller Capacitor Voltage, Vehicle Speed, Motor Velocity, SOC, Time Charging, Time Operating, Vehicle Run Hours \n')

            for line in f:

                data = line.strip().split(" ")
                print data
                print (len(data))
                if (len(data) == 19 or len(data) == 23): #time stamp + 18/22 data points
                    parse_data(file, data)

        #Write summations to first and second lines in the .csv file.
        excelFile = open(fileName, 'r+')
        excelFile.seek(0)
        excelFile.write('Date, Odometer, Battery Energy, Motor Energy, Auxiliary Energy, Hours Charging, Hours Running, Hours On\n')
        excelFile.write(parse_date(fileName[:-4]) +  ',' + str(odometer) +  ',' + str(battery_energy) +  ',' + str(motor_energy) +  ',' + str(aux_energy) +  ',' + str(hours_charging) +  ',' + str(hours_running) +  ',' + str(hours_operating))
        excelFile.close()

        #If summary file doesn't exist: make it and the write the header!
        if (not os.path.exists("Summary.csv")):
            with open("Summary.csv", 'a+') as summaryFile:
                summaryFile.write('Date, Odometer, Battery Energy, Motor Energy, Auxiliary Energy, Hours Charging, Hours Running, Hours On')

        #Append summations to summary file
        with open("Summary.csv", 'a+') as summaryFile:
            summaryFile.write("\n" + parse_date(fileName[:-4]) +  ',' + str(odometer) +  ',' + str(battery_energy) +  ',' + str(motor_energy) +  ',' + str(aux_energy) +  ',' + str(hours_charging) +  ',' + str(hours_running) +  ',' + str(hours_operating))
            
        #move files into the done folder after processing them
        #shutil.move('Datalogs/' + file, 'Datalogs/RAW/' + file)
        print("Moved file: " + file)
