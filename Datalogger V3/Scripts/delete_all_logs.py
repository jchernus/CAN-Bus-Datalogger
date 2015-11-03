import sys, sqlite3

db_path = "/data/databases/Logs.db"

#create database 
conn=sqlite3.connect(db_path)
curs=conn.cursor()
#curs.execute("""DELETE FROM dailylogs""")
curs.execute("""DROP TABLE dailyLogs;""")
curs.execute("""DELETE FROM days;""")
curs.execute("""DELETE FROM faults;""")
curs.execute("VACUUM;")
conn.commit()
curs.execute("""CREATE TABLE `dailyLogs` (
	`date`	TEXT,
	`time`	TEXT,
	`soc`	INTEGER,
	`battery_current`	REAL,
	`battery_voltage`	REAL,
	`battery_power_out`	REAL,
	`battery_power_in`	REAL,
	`motor_current`	REAL,
	`motor_voltage`	REAL,
	`mc_battery_current`	INTEGER,
	`mc_cap_voltage`	REAL,
	`vehicle_speed`	REAL,
	`motor_velocity`	INTEGER,
	`fault`	INTEGER,
	`traction_state`	INTEGER,
	`maximum_discharge`	INTEGER,
	`maximum_charge`	INTEGER,
	`motor_temp`	REAL,
	`mc_heatsink_temp`	REAL,
	`battery_high_temp`	REAL,
	`batt_high_temp_id`	INTEGER,
	`batt_low_temp`	REAL,
	`batt_low_temp_id`	INTEGER,
	`pluggen_in`	INTEGER,
	`charging`	INTEGER,
	`operating`	INTEGER,
	`running`	INTEGER
);""")
conn.commit()
print "success"

