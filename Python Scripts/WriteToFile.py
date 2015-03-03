import os, shutil

#confirm your original path
print("Path at terminal when executing this file")
print(os.getcwd() + "\n")

#create the paths that are needed to store files
if (not os.path.exists("Datalogs")):
    os.mkdir("Datalogs")
if (not os.path.exists("Datalogs/RAW")):
    os.mkdir("Datalogs/RAW")

def parse_data(fileName, data):

    #convert variables from byte-strings to ints/floats
    battery_current = int(data[2] + data[1], 16)/10
    battery_voltage = int(data[4] + data[3], 16)/100
    mc_cap_voltage = int(data[6] + data[5], 16)/16
    motor_current = int(data[8] + data[7], 16)

    motor_voltage = int(data[10] + data[9], 16)
    mc_battery_current = int(data[12] + data[11], 16)
    vehicle_speed = int(data[14] + data[13], 16)
    motor_velocity = int(data[18] + data[17] + data[16] + data[15], 16)

    if (len(data) > 18):
        soc = int(data[20] + data[19], 16)/2

        data_21 = str(bin(int(data[21], 16)))[2:]
        while (len(data_21) < 16):
            data_21 = '0' + data_21

        time_charging = data_21[2]
        vehicle_on_time = data_21[3]

        run_hours = int(data[22], 16)


    #write values to excel
    excelFile.write(data[0] + ",")                                      #Time Stamp
    excelFile.write(str(battery_current) + ",")                         #Battery Current
    excelFile.write(str(battery_voltage) + ",")                         #Battery Voltage
    excelFile.write("POWER ,")
    #excelFile.write("=PRODUCT(INDIRECT(ADDRESS(ROW() \
    #    ,COLUMN()-1)),INDIRECT(ADDRESS(ROW(),COLUMN()-2)))")           #Battery Power Formula
    excelFile.write(str(mc_cap_voltage) + ",")                          #Motor Controller Capacitor Voltage
    excelFile.write(str(motor_current) + ",")
    excelFile.write(str(motor_voltage) + ",")
    excelFile.write(str(mc_battery_current) + ",")
    excelFile.write(str(vehicle_speed) + ",")
    excelFile.write(str(motor_velocity) + ",")

    if (len(data) > 18):
        excelFile.write(str(soc) + ",")
        excelFile.write(str(time_charging) + ",")
        excelFile.write(str(vehicle_on_time) + ",")
        excelFile.write(str(run_hours) + ",")

#process all of the files in the Datalogs directory that end in .txt
for file in os.listdir("Datalogs"):
    if file.endswith(".txt"):
        with open(file, 'r+') as f: #open files as read only

            #create & start the excel file that will house the parsed data
            fileName = "Datalogs/" + file[:len(file)-4] + ".csv"
            excelFile = open(fileName, 'a+')
            excelFile.write('Time Stamp, Battery Amperage, Battery Voltage, Battery Power, Motor Controller Capacitor Voltage, Motor Current, Motor Voltage, Motor Controller Battery Current, Vehicle Speed, Motor Velocity, SOC, Time Charging, Time Operating, Vehicle Run Hours \n')

            for line in f:

                data = line.strip().split(" ")
                print data
                print (len(data))
                if (len(data) == 19 or len(data) == 23): #time stamp + 18/22 data points
                    parse_data(file, data)

                #f.write("Python is a great language.\nYeah its great!!\n");

        #move files into the done folder after processing them
        excelFile.close()
        #shutil.move('Datalogs/' + file, 'Datalogs/RAW/' + file)
        print("Moved file: " + file)


