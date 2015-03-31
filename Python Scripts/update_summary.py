#!/usr/bin/python

import os, sys

cmdargs = sys.argv[1:] # list of files that end in .csv and were not modified in the last hour

for file in cmdargs:
	print file
	with open(file, 'r+') as parsedFile:
		line = parsedFile.readline() #ignore the first line
		line = parsedFile.readline() #we want this second line
		sums = line.strip().split(",")

		date = sums[0]
		odometer = float(sums[1])
		battery_energy_operating = float(sums[2])
		battery_energy_charging = float(sums[3])
		hours_charging = float(sums[4])
		hours_operating = float(sums[5])
		hours_running = float(sums[6])
		
		#If summary file doesn't exist: make it and then write the header!
		if (not os.path.exists("/data/summary/Summary.csv")):
			with open("/data/summary/Summary.csv", 'a+') as summaryFile:
				summaryFile.write('Date, Odometer [km], Battery Energy Out (Operating) [kJ], Battery Energy In (Charging)[kJ], Hours Charging [h], Hours Operating [h], Hours Running [h]')

		#Append summations to summary file
		with open("/data/summary/Summary.csv", 'a+') as summaryFile:
			summaryFile.write("\n" + date +  ',' + str(odometer) +  ',' + str(battery_energy_operating) +  ',' + str(battery_energy_charging) +  ',' + str(hours_charging) +  ',' + str(hours_operating) +  ',' + str(hours_running))
	os.rename(file, file[:16] + file[17:]) # rename the file to remove the '_'