import subprocess, os, re, sys, sqlite3

path = "/data/dailylogs/"

print sys.argv
files = sys.argv[1:]

for file in files:
	dbname = "DailyLogs.db"
	
	try:
		os.remove(dbname)
	except:
		pass

	#create database 
	conn=sqlite3.connect(path + dbname)
	curs=conn.cursor()
	
	curs.execute("""CREATE TABLE log (date TEXT, time TEXT, soc INTEGER, battery_current REAL, battery_voltage REAL, 
	battery_power_out REAL, battery_power_in REAL, motor_current REAL, motor_voltage REAL, 
	mc_cap_voltage REAL, vehicle_speed REAL, motor_velocity INTEGER, fault INTEGER, traction_state INTEGER,
	maximum_discharge INTEGER, maximum_charge INTEGER, motor_temp REAL, mc_heatsink_temp REAL, battery_high_temp REAL,
	batt_high_temp_id INTEGER, batt_low_temp REAL, batt_low_temp_id INTEGER, charging INTEGER, operating INTEGER,
	running INTEGER)""")
	
	#curs.execute("""CREATE TABLE log (date TEXT, odometer REAL, energy_in REAL, energy_out REAL, 
	#hours_charging REAL, hours_operating REAL, hours_running REAL)""")
	
	conn.commit()
	
	filename = path + str(file)
	with open (filename) as textLog:
		for line in textLog:
			data = line.split(',')
			str = "INSERT INTO log values('"
			for datum in data:
				str += datum.strip() + "','"
			str = str[:-2] #get rid of that last comma
			str += ")"
			curs.execute(str)
		
		conn.commit()
		conn.close()
