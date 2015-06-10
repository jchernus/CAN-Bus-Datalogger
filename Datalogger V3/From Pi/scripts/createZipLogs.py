#!/usr/bin/env python

import sqlite3, os, sys, subprocess

dates = sys.argv[1:] # Retrieve the requested dates

db_path = "/data/databases/DailyLogs.db"
csv_path = "/var/tmp/logs/"

#check the date, set the filename
p = subprocess.Popen("date +\"%Y-%m-%d_%H-%M-%S\"", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
todayDateTime = output.strip()
today = todayDateTime[:10]

if (os.path.exists(db_path)):

	#Connect to Database
	conn = sqlite3.connect(db_path)
	curs = conn.cursor()

	#Create each day's CSV file
	for date in dates:
			if not os.path.exists(csv_path + str(date) + ".csv"): #Path does not exist, or date is today's so lets remake it anyway.
					filename = date
					if (date == today):
							filename += "_incomplete"
					filename += ".csv"
					with open(csv_path + filename, 'w+') as file:
							file.write('Time Stamp, SOC [%], Battery Current [A], Battery Voltage [V], Battery Power Out (Operating) [kW], Battery Power In (Charging)[kW], Motor Current [AC A rms], Motor Voltage [AC V rms], Motor Controller Capacitor Voltage [V], Vehicle Speed [km/h], Motor Velocity [RPM], Current Highest Priority Fault, Traction State, Maximum Battery Discharge Current [A], Maximum Battery Charge Current [A], Motor Temperature [Celcius], Motor Controller Heatsink Temperature [Celcius], Battery Pack Highest Temperature [Celcius], Batt High Temp ID, Batter Pack Lowest Temperature [Celcius], Batt Low Temp ID, Charging, Operating, Running\n')
							for row in curs.execute("SELECT * FROM log WHERE date = '" + str(date).strip() + "' ORDER BY time"):
									str_row = ' '.join([str(line).strip() + "," for line in row]).strip() + "\n"
									file.write(str_row)

	conn.close()

	#Zip files
	p = subprocess.Popen("zip " + csv_path + todayDateTime + ".zip " + ' '.join(date + ".csv" for date in dates), stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	
	print todayDateTime + ".zip"
        
else:
        #How to say that things failed?
        raise IOError('Database file does not exist.')
		

