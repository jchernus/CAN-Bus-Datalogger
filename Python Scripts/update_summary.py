#!/usr/bin/python

import os, sys

cmdargs = sys.argv[1:] # list of files that end in .csv and were not modified in the last hour

for file in cmdargs:
    if file != "/data/scripts/Datalogs/Summary.csv":
        with open(file, 'r+') as parsedFile:
            line = parsedFile.readline() #ignore the first line
            line = parsedFile.readline() #we want this second line
            sums = line.strip().split(",")

            date = sums[0]
            odometer = float(sums[1])
            battery_energy = float(sums[2])
            motor_energy = float(sums[3])
            aux_energy = float(sums[4])
            hours_charging = float(sums[5])
            hours_running = float(sums[6])
            hours_operating = float(sums[7])
                    
            #If summary file doesn't exist: make it and then write the header!
            if (not os.path.exists("/data/scripts/Datalogs/Summary.csv")):
                with open("/data/scripts/Datalogs/Summary.csv", 'a+') as summaryFile:
                    summaryFile.write('Date, Odometer, Battery Energy, Motor Energy, Auxiliary Energy, Hours Charging, Hours Running, Hours On')

            #Append summations to summary file
            with open("/data/scripts/Datalogs/Summary.csv", 'a+') as summaryFile:
                summaryFile.write("\n" + date +  ',' + str(odometer) +  ',' + str(battery_energy) +  ',' + str(motor_energy) +  ',' + str(aux_energy) +  ',' + str(hours_charging) +  ',' + str(hours_running) +  ',' + str(hours_operating))
