import sys, sqlite3

db_path = "/data/databases/Logs.db"

#create database 
conn=sqlite3.connect(db_path)
curs=conn.cursor()
#curs.execute("""DELETE FROM dailylogs""")
curs.execute("""DROP TABLE dailyLogs;""")
curs.execute("""DELETE FROM days;""")
curs.execute("VACUUM;")
conn.commit()
curs.execute("""CREATE TABLE `dailyLogs` (
	`date`	TEXT,
	`time`	TEXT,
	`soc`	NUMERIC,
	`battery_current`	NUMERIC,
	`battery_voltage`	NUMERIC,
	`battery_power_out`	NUMERIC,
	`battery_power_in`	NUMERIC,
	`motor_current`	NUMERIC,
	`motor_voltage`	NUMERIC,
	`mc_battery_current`	NUMERIC,
	`mc_cap_voltage`	NUMERIC,
	`vehicle_speed`	NUMERIC,
	`motor_velocity`	NUMERIC,
	`fault`	INTEGER,
	`traction_state`	INTEGER,
	`maximum_discharge`	INTEGER,
	`maximum_charge`	INTEGER,
	`motor_temp`	NUMERIC,
	`mc_heatsink_temp`	NUMERIC,
	`batt_high_temp`	INTEGER,
	`batt_high_temp_id`	INTEGER,
	`batt_low_temp`	INTEGER,
	`batt_low_temp_id`	INTEGER,
	`high_cell_voltage`	NUMERIC,
	`high_cell_voltage_id`	INTEGER,
	`low_cell_voltage`	NUMERIC,
	`low_cell_voltage_id`	INTEGER,
	`plugged_in`	INTEGER,
	`charging`	INTEGER,
	`operating`	INTEGER,
	`running`	INTEGER
);""")
conn.commit()
print "success"

