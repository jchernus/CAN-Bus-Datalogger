#!/usr/bin/env python

import sqlite3, os, subprocess, re

db_path = "/data/databases/Battery.db"
current_date = ""
cell_voltages = [0.0] * 96
batt_stats = [[0.0] * 3] * 4
pack_voltage = pack_soc = total_pack_cycles = 0.0

PIDs = ['F100','F101', 'F103', 'F104', 'F106', 'F107', 'F109', 'F10A']
cellVDict = {}

def parse_data():
        global pack_voltage, pack_soc, total_pack_cycles, cell_voltages

        for PID in PIDS:

                #remove whitespaces entirely
                pattern = re.compile(r'\s+')
                cellVDict[PID] = re.sub(pattern, '', cellVDict[PID])

                if "F0" in PID:         #it's a battery pack field
                        if PID == "F00D":
                                pack_voltage = int(data[8] + data[9] + data[10] + data[11], 16) * 0.1
                        elif PID == "F00F":
                                pack_soc = int(data[8] + data[9], 16) * 0.5
                        elif PID == "F018":
                                total_pack_cycles = int(data[8] + data[9] + data[10] + data[11], 16)
                elif "F1" in PID:
                        data = cellVDict[PID][10:] #remove header
                        if PID == "F100":
                                for x in range (0,12):
                                        i = x * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_voltages[x] = voltage
                                        if voltage > battery_stats[0][1]:
                                                battery_stats[0][1] = voltage
                                        elif voltage < battery_stats[0][2]:
                                                battery_stats[0][2] = voltage
                                        battery_stats[0][0] = battery_stats[0][0] + voltage
                        elif PID == "F101":
                                for x in range (12,23):
                                        i = (x - 12) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_voltages[x] = voltage
                                        if voltage > battery_stats[0][1]:
                                                battery_stats[0][1] = voltage
                                        elif voltage < battery_stats[0][2]:
                                                battery_stats[0][2] = voltage
                                        battery_stats[0][0] = battery_stats[0][0] + voltage
                                        
                        elif PID == "F103":
                                for x in range (24,35):
                                        i = (x - 24) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_voltages[x] = voltage
                                        if voltage > battery_stats[1][1]:
                                                battery_stats[1][1] = voltage
                                        elif voltage < battery_stats[1][2]:
                                                battery_stats[1][2] = voltage
                                        battery_stats[1][0] = battery_stats[1][0] + voltage
                        elif PID == "F104":
                                for x in range (36,47):
                                        i = (x - 36) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_voltages[x] = voltage
                                        if voltage > battery_stats[1][1]:
                                                battery_stats[1][1] = voltage
                                        elif voltage < battery_stats[1][2]:
                                                battery_stats[1][2] = voltage
                                        battery_stats[1][0] = battery_stats[1][0] + voltage
                                        
                        elif PID == "F106":
                                for x in range (48,59):
                                        i = (x - 48) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_voltages[x] = voltage
                                        
                                        if voltage > battery_stats[2][1]:
                                                battery_stats[2][1] = voltage
                                        elif voltage < battery_stats[2][2]:
                                                battery_stats[2][2] = voltage
                                        battery_stats[2][0] = battery_stats[2][0] + voltage
                        elif PID == "F107":
                                for x in range (60,71):
                                        i = (x - 60) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_voltages[x] = voltage
                                        
                                        if voltage > battery_stats[2][1]:
                                                battery_stats[2][1] = voltage
                                        elif voltage < battery_stats[2][2]:
                                                battery_stats[2][2] = voltage
                                        battery_stats[2][0] = battery_stats[2][0] + voltage
                                        
                        elif PID == "F109":
                                for x in range (72,83):
                                        i = (x - 72) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_voltages[x] = voltage
                                        
                                        if voltage > battery_stats[3][1]:
                                                battery_stats[3][1] = voltage
                                        elif voltage < battery_stats[3][2]:
                                                battery_stats[3][2] = voltage
                                        battery_stats[3][0] = battery_stats[3][0] + voltage
                        elif PID == "F10A":
                                for x in range (84,95):
                                        i = (x - 84) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_voltages[x] = voltage
                                        
                                        if voltage > battery_stats[3][1]:
                                                battery_stats[3][1] = voltage
                                        elif voltage < battery_stats[3][2]:
                                                battery_stats[3][2] = voltage
                                        battery_stats[3][0] = battery_stats[3][0] + voltage
                else:
                        print "Error: Unknown CAN Message. Message: " + cellVDict[PID]
                        break

        #divide sums by 24 to get the average        
        for j in range (0,4):
                battery_stats[j][0] = battery_stats[j][0] / 24.0

def update_database():
        global current_date
        
        #get current date & time
        p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True) 
        (output, err) = p.communicate()
        current_date = output

        for PID in PIDS:
                #send request for cell voltages
                p = subprocess.Popen("./cansend can0 7E3#0422" + PID + "00000000", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()

                #receive message
                p = subprocess.Popen("./candump -t A -n 1 can0,7EB:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()

                cellVDict[PID] = output.strip().split("  ")[3][3:].strip()
                
                if ("7EB 10__62F1") in output:          #cell voltages                                                                                          #Update values once known

                        #send request for more data
                        p = subprocess.Popen("./cansend can0 7E3#30", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                        (output, err) = p.communicate()

                        #receive remaining message
                        p = subprocess.Popen("./candump -t A -n 3 can0,7EB:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                        (output, err) = p.communicate()
                        lines = output.strip().split("\n")
                        
                        #parse messages
                        for line in lines:
                                try:
                                    data = line.strip().split("  ")
                                    cellVDict[PID] = cellVDict[PID] + " " + data[3][3:].strip()                                                               #Grab just the cell voltage data, no headers
                                except:
                                    print "Error: unable to parse line. Line: " + line
                                    pass
                elif ("7EB 10__62F0") in output:        #pack data
                        #all data acquired
                        cellVDict[PID] = output.strip().split("  ")[3][3:].strip()                                                                            #Am I grabbing the correct data?
                else:
                        #ERROR
                        print "Error: did not receive reply from BMS."
                        break

        parse_data()        

        #Write to database
        curs.execute("DELETE FROM summary;")
        curs.execute("VACUUM;")
        
        command = "INSERT INTO summary VALUES('"
        command += current_date[:11] + "','" + current_date[11:19] + "','"
        command += pack_voltage
        command += pack_soc
        command += total_pack_cycles

        for j in range (0,4):
                for k in range (0,3):
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
