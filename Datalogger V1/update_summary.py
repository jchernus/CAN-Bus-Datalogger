#!/usr/bin/python

import os, sys

cmdargs = sys.argv[1:] # list of files that end in .csv and were not modified in the last hour

for file in cmdargs:
	print file
	with open(file, 'r+') as parsedFile:
		line = parsedFile.readline() #ignore the first line
		line = parsedFile.readline() #we want this second line
		sums = line.strip().split(",")

		date = odometer = battery_energy_operating = battery_energy_charging = hours_charging = hours_operating = hours_running = None

		try:
			date = sums[0]
		except:
			date = "Error"
		try:
			odometer = float(sums[1])
		except:
			odometer = "Error"
		try:
			battery_energy_operating = float(sums[2])
		except:
			battery_energy_operating = "Error"
		try:
			battery_energy_charging = float(sums[3])
		except:
			battery_energy_charging = "Error"
		try:
			hours_charging = float(sums[4])
		except:
			hours_charging = "Error"
		try:
			hours_operating = float(sums[5])
		except:
			hours_operating = "Error"
		try:
			hours_running = float(sums[6])
		except:
			hours_running = "Error"
		
		#If summary file doesn't exist: make it and then write the header!
		if (not os.path.exists("/data/summary/Summary.csv")):
			with open("/data/summary/Summary.csv", 'a+') as summaryFile:
				summaryFile.write('Date, Odometer [km], Battery Energy Out (Operating) [kWh], Battery Energy In (Charging)[kWh], Hours Charging [h], Hours Operating [h], Hours Running [h]')

		#Append summations to summary file
		with open("/data/summary/Summary.csv", 'a+') as summaryFile:
			summaryFile.write("\n" + date +  ',' + str(odometer) +  ',' + str(battery_energy_operating) +  ',' + str(battery_energy_charging) +  ',' + str(hours_charging) +  ',' + str(hours_operating) +  ',' + str(hours_running))
	os.rename(file, file[:16] + file[17:]) # rename the file to remove the '_'
