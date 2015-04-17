import subprocess, os, sys

#Create the paths that are needed to store files
if (not os.path.exists("/data/dailylogs")):
    os.mkdir("/data/dailylogs")

#Check the date
p = subprocess.Popen("date", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
print "Today is", output

#Filename based on date
filename = ""

#Does a file for today's date already exist?
if os.path.exists("/data/dailylogs"):
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
    excelFile = open(path + fileName, 'a+')
    if not file_existed: #the file was just created, add the top column headings
        excelFile.write('\n                                                                                                                                                                                                                          ')
        excelFile.write('\n                                                                                                                                                                                                                                                ')
        excelFile.write('\n\nTime Stamp, Battery Current [A], Battery Voltage [V], Battery Power Out (Operating) [kW], Battery Power In (Charging)[kW], Motor Current [AC A rms], Motor Voltage [AC V rms], Vehicle Speed [km/h], Motor Velocity [RPM], SOC [%], Charging, Operating, Running\n')

