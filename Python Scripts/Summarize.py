import os

def parse_date(date):
    if int(date[0:1]) < 5:
        year = "202" + date[0:1]
    else:
        year = "201" + date[0:1]
    day = str(int(date[4:6]))
    
    date = date[1:4].upper()
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


fileName = "5MAR05.csv"
if os.path.exists(fileName):
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
                
        #If summary file doesn't exist: make it and then write the header!
        if (not os.path.exists("Summary.csv")):
            with open("Summary.csv", 'a+') as summaryFile:
                summaryFile.write('Date, Odometer, Battery Energy, Motor Energy, Auxiliary Energy, Hours Charging, Hours Running, Hours On')

        #Append summations to summary file
        with open("Summary.csv", 'a+') as summaryFile:
            summaryFile.write("\n" + parse_date(fileName[:-4]) +  ',' + str(odometer) +  ',' + str(battery_energy) +  ',' + str(motor_energy) +  ',' + str(aux_energy) +  ',' + str(hours_charging) +  ',' + str(hours_running) +  ',' + str(hours_operating))
