#!/usr/bin/env python

import sqlite3, os, subprocess

db_path = "/data/databases/Battery.db"
cell_voltages = [0.0] * 96
batt_stats = [[0.0] * 4] * 4
pack_voltage = pack_soc = total_pack_cycles = 0.0

def parse_data(msg_id, data):
        global pack_voltage, pack_soc, total_pack_cycles, cell_voltages

        if (msg_id == "F00D"):
                pack_voltage = int(data[2] + data[3] + data[0] + data[1], 16) * 0.1
        elif (msg_id == "F00F"):
                pack_soc = int(data[0] + data[1], 16) * 0.5
        elif (msg_id == "F018"):
                total_pack_cycles = int(data[2] + data[3] + data[0] + data[1], 16)
        else:
                offset = 0
                
                if (msg_id == "F100"): offset = 0
                elif (msg_id == "F101"): offset = 12
                elif (msg_id == "F102"): offset = 24
                elif (msg_id == "F103"): offset = 36
                elif (msg_id == "F104"): offset = 48
                elif (msg_id == "F105"): offset = 60
                elif (msg_id == "F106"): offset = 72
                elif (msg_id == "F107"): offset = 84
                
                for i in range (0, 12):
                        cell_voltages[i+offset] = int(data[2*i] + data[2*i+1], 16) * 0.0001

def update_database():
        
        #send request for messages
        p = subprocess.Popen("./cansend can0 F100#; ./cansend can0 F101#; ./cansend can0 F102#", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
        (output2, err2) = p.communicate()

        #receive messages
        p = subprocess.Popen("./candump -t A -n 8 can0,F100:7ff,F101:7ff,F102:7ff,F103:7ff,F104:7ff,F105:7ff,F106:7ff,F107:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        #parse messages
        lines = output.strip().split("\n")
        for line in lines:
            try:
                data = line.strip().split("  ")
                parse_data(data[2], data[3][3:].strip()) #time stamp, message id, message
            except:
                print "Error parsing line: " + line
                pass

        #Do some calculations
        for j in range (0,4):
                pack_max = pack_min = pack_avg
                for k in range (0,24):
                        if cell_voltage[k + 24*j] > pack_max:
                                pack_max = cell_voltage[k + 24*j]
                        elif cell_voltage[k + 24*j] < pack_min:
                                pack_min = cell_voltage[k + 24*j]
                        pack_avg += cell_voltage[k + 24*j]
                batt_stats[j][0] = pack_avg/24.0
                batt_stats[j][1] = pack_max
                batt_stats[j][2] = pack_min

        #Write to database
        p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True) 
        (output, err) = p.communicate()
        current_date = output

        curs.execute("DELETE FROM summary;")
        curs.execute("VACUUM;")
        
        command = "INSERT INTO summary VALUES('"
        command += current_date[:11] + "','" + current_date[11:19] + "','"
        command += pack_voltage
        command += pack_soc
        command += total_pack_cycles

        for j in range (0,4):
                for k in range (0,4):
                        command += batt_stats[j][k] + "','"
        
        for i in range (0,96):
                command += cell_voltages[i] + "','"
        command = command[:-2] + "');"
        curs.execute(command)
        
        print "success"

#record messages
conn = sqlite3.connect(db_path)
curs = conn.cursor()

if (os.path.exists(db_path)):
        curs.execute("SELECT date, time FROM battery LIMIT 1")
        data = curs.fetchall()
        datumDate = data[0][0]
        datumTime = data[0][1]

        needRefresh = False
        
        #check time, if less than 1 minute ago, good
        p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True) 
        (output, err) = p.communicate()
        current_date = output

        if (datumDate != current_date[:10] or (datumTime != current_date[11:16])):
                update_database()
        else:
                print "success"
    
else:
	curs.execute("""CREATE TABLE battery(date DATE, time TIME, packVoltage REAL, packSOC INTEGER, 
        batt1Avg REAL, batt1High REAL, batt1Low REAL, batt1Temp REAL, 
        batt2Avg REAL, batt2High REAL, batt2Low REAL, batt2Temp REAL, 
        batt3Avg REAL, batt3High REAL, batt3Low REAL, batt3Temp REAL, 
        batt4Avg REAL, batt4High REAL, batt4Low REAL, batt4Temp REAL, 
        cell1 REAL, cell2 REAL, cell3 REAL, cell4 REAL, cell5 REAL, cell6 REAL, cell7 REAL, cell8 REAL, cell9 REAL, cell10 REAL, cell11 REAL, cell12 REAL,
        cell13 REAL, cell14 REAL, cell15 REAL, cell16 REAL, cell17 REAL, cell18 REAL, cell19 REAL, cell20 REAL, cell21 REAL, cell22 REAL, cell23 REAL, cell24 REAL,
        cell25 REAL, cell26 REAL, cell27 REAL, cell28 REAL, cell29 REAL, cell30 REAL, cell31 REAL, cell32 REAL, cell33 REAL, cell34 REAL, cell35 REAL, cell36 REAL,
        cell37 REAL, cell38 REAL, cell39 REAL, cell40 REAL, cell41 REAL, cell42 REAL, cell43 REAL, cell44 REAL, cell45 REAL, cell46 REAL, cell47 REAL, cell48 REAL,
        cell49 REAL, cell50 REAL, cell51 REAL, cell52 REAL, cell53 REAL, cell54 REAL, cell55 REAL, cell56 REAL, cell57 REAL, cell58 REAL, cell59 REAL, cell60 REAL,
        cell61 REAL, cell62 REAL, cell63 REAL, cell64 REAL, cell65 REAL, cell66 REAL, cell67 REAL, cell68 REAL, cell69 REAL, cell70 REAL, cell71 REAL, cell72 REAL,
        cell73 REAL, cell74 REAL, cell75 REAL, cell76 REAL, cell77 REAL, cell78 REAL, cell79 REAL, cell80 REAL, cell81 REAL, cell82 REAL, cell83 REAL, cell84 REAL,
        cell85 REAL, cell86 REAL, cell87 REAL, cell88 REAL, cell89 REAL, cell90 REAL, cell91 REAL, cell92 REAL, cell93 REAL, cell94 REAL, cell95 REAL, cell96 REAL		
        )""")

	conn.commit()

	#Fill it with stuff!
	update_database()

conn.commit()
conn.close()
