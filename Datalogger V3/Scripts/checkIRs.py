#!/usr/bin/env python

import sqlite3, os, subprocess, re

db_path = "/data/databases/Battery.db"
current_date = ""
cell_IRs = [0.0] * 96
batt1_stats = [0.0, 0.0, 4.0]
batt2_stats = [0.0, 0.0, 4.0]
batt3_stats = [0.0, 0.0, 4.0]
batt4_stats = [0.0, 0.0, 4.0]
battHighTemp, battLowTemp, battHighTempId, battLowTempId = 0, 0, 0, 0
pack_voltage = pack_soc = total_pack_cycles = 0.0

PIDs = ['F300','F301', 'F303', 'F304', 'F306', 'F307', 'F309', 'F30A', 'F00D', 'F00F', 'F018']
cellIRDict = {}

def parse_message(msg_id, data):
        global battHighTemp, battLowTemp, battHighTempId, battLowTempId

        if (msg_id == "479" or msg_id == "480"):     # these two transmit the same info
                battHighTemp = int(data[0] + data[1], 16)
                battLowTemp = int(data[4] + data[5], 16)
                battHighTempId = int(data[8] + data[9], 16)
                battLowTempId = int(data[10] + data[11], 16)

def parse_data():
        global pack_voltage, pack_soc, total_pack_cycles, cell_IRs, batt_stats

        for PID in PIDs:
            
                #remove whitespaces entirely
                pattern = re.compile(r'\s+')
                cellIRDict[PID] = re.sub(pattern, '', cellIRDict[PID])

                if "F0" in PID:         #it's a battery pack field
                        data = cellIRDict[PID]
                        if PID == "F00D":
                                pack_voltage = int(data[8] + data[9] + data[10] + data[11], 16) * 0.1
                        elif PID == "F00F":
                                pack_soc = int(data[8] + data[9], 16) * 0.5
                        elif PID == "F018":     
                                total_pack_cycles = int(data[8] + data[9] + data[10] + data[11], 16)

                elif "F1" in PID:       #cell voltages
                        data = cellIRDict[PID][10:] #remove header
                        if PID == "F300":
                                for x in range (0,12):
                                        i = x * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_IRs[x] = voltage
                                        if voltage > batt1_stats[1]:
                                                batt1_stats[1] = voltage
                                        elif voltage < batt1_stats[2]:
                                                batt1_stats[2] = voltage
                                        batt1_stats[0] = batt1_stats[0] + voltage
                        elif PID == "F301":
                                for x in range (12,24):
                                        i = (x - 12) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_IRs[x] = voltage
                                        if voltage > batt1_stats[1]:
                                                batt1_stats[1] = voltage
                                        elif voltage < batt1_stats[2]:
                                                batt1_stats[2] = voltage
                                        batt1_stats[0] = batt1_stats[0] + voltage
                        elif PID == "F303":
                                for x in range (24,36):
                                        i = (x - 24) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_IRs[x] = voltage
                                        if voltage > batt2_stats[1]:
                                                batt2_stats[1] = voltage
                                        elif voltage < batt2_stats[2]:
                                                batt2_stats[2] = voltage
                                        batt2_stats[0] = batt2_stats[0] + voltage
                        elif PID == "F304":
                                for x in range (36,48):
                                        i = (x - 36) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        
                                        cell_IRs[x] = voltage
                                        if voltage > batt2_stats[1]:
                                                batt2_stats[1] = voltage
                                        elif voltage < batt2_stats[2]:
                                                batt2_stats[2] = voltage
                                        batt2_stats[0] = batt2_stats[0] + voltage
                                        
                        elif PID == "F306":
                                for x in range (48,60):
                                        i = (x - 48) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_IRs[x] = voltage
                                        
                                        if voltage > batt3_stats[1]:
                                                batt3_stats[1] = voltage
                                        elif voltage < batt3_stats[2]:
                                                batt3_stats[2] = voltage
                                        batt3_stats[0] = batt3_stats[0] + voltage
                        elif PID == "F307":
                                for x in range (60,72):
                                        i = (x - 60) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_IRs[x] = voltage
                                        
                                        if voltage > batt3_stats[1]:
                                                batt3_stats[1] = voltage
                                        elif voltage < batt3_stats[2]:
                                                batt3_stats[2] = voltage
                                        batt3_stats[0] = batt3_stats[0] + voltage
                                        
                        elif PID == "F309":
                                for x in range (72,84):
                                        i = (x - 72) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_IRs[x] = voltage
                                        
                                        if voltage > batt4_stats[1]:
                                                batt4_stats[1] = voltage
                                        elif voltage < batt4_stats[2]:
                                                batt4_stats[2] = voltage
                                        batt4_stats[0] = batt4_stats[0] + voltage
                        elif PID == "F30A":
                                for x in range (84,96):
                                        i = (x - 84) * 4
                                        voltage = int(data[i] + data[i+1] + data[i+2] + data[i+3], 16) * 0.0001
                                        cell_IRs[x] = voltage
                                        
                                        if voltage > batt4_stats[1]:
                                                batt4_stats[1] = voltage
                                        elif voltage < batt4_stats[2]:
                                                batt4_stats[2] = voltage
                                        batt4_stats[0] = batt4_stats[0] + voltage

        #divide sums by 24 to get the average        
        batt1_stats[0] = batt1_stats[0] / 24.0
        batt2_stats[0] = batt2_stats[0] / 24.0        
        batt3_stats[0] = batt3_stats[0] / 24.0
        batt4_stats[0] = batt4_stats[0] / 24.0

def update_database():
        global current_date

        for PID in PIDs:
                #send request for cell voltages
                p = subprocess.Popen("(sleep 0.1; ./cansend can0 7E3#0422" + PID + "00000000) &", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)

                #receive message
                p = subprocess.Popen("timeout 1 ./candump -t A -n 1 can0,7EB:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()

                if len(output) > 0:  # got the response message

                        cellIRDict[PID] = output.strip().split("  ")[3][3:].strip()
                        
                        if ("7EB  [8] 10 1B 62 F3" in output):          #cell voltages                                                                                          #Update values once known
                                #send request for more data
                                p = subprocess.Popen("(sleep 0.1; ./cansend can0 7E3#30) &", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)

                                #receive remaining message
                                p = subprocess.Popen("timeout 2 ./candump -t A -n 3 can0,7EB:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                                (output, err) = p.communicate()

                                if len(output) > 0:  # got the response message
                                
                                        lines = output.strip().split("\n")
                                        
                                        #parse messages
                                        for line in lines:
                                                try:
                                                    data = line.strip().split("  ")
                                                    cellIRDict[PID] = cellIRDict[PID] + " " + data[3][3:].strip()[3:]  
                                                except:
                                                    return "Error: unable to parse line. Line: " + line
                                else:
                                        return "Error: did not receive additional messages from BMS."
                                
                        elif ("7EB  [8] 04 62 F0" in output) or ("7EB  [8] 05 62 F0" in output):        #pack data
                                #all data acquired
                                cellIRDict[PID] = output.strip().split("  ")[3][3:].strip()
                        else:
                                pass
                                #print "Error: cannot decode reply from BMS."
                else:
                        print "Timed out."
                        return "Error: did not receive reply from BMS."

        #retrieve pack temperature information
        p = subprocess.Popen("timeout 2 ./candump -t A -n 1 can0,479:7ff,480:7ff", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        if len(output) > 0:  # got the response message
                lines = output.strip().split("\n")
                
                data = lines[0].strip().split("  ")
                parse_message(data[2], data[3][3:].strip()) #message id, message data
        else:
                #ERROR
                return "Error: did not receive 479/480 temperature message from BMS."

        #parse all of the data
        try:
                parse_data()
        except:
                return "Error parsing data."

        #print "\nBATTERY STATS"
        #print batt1_stats
        #print batt2_stats
        #print batt3_stats
        #print batt4_stats

        #Write to database
        curs.execute("DELETE FROM IR;")
        curs.execute("VACUUM;")
        
        command = "INSERT INTO IR VALUES('"
        command += current_date[:11] + "','" + current_date[11:19] + "','"
        command += str(pack_voltage) + "','"
        command += str(pack_soc) + "','"
        command += str(total_pack_cycles) + "','"
		
	command += str(battHighTemp) + "','" + str(battLowTemp) + "','" + str(battHighTempId) + "','" + str(battLowTempId) + "','"

        for j in range (0,3):
                command += str(batt1_stats[j]) + "','"
        for j in range (0,3):
                command += str(batt2_stats[j]) + "','"
        for j in range (0,3):
                command += str(batt3_stats[j]) + "','"
        for j in range (0,3):
                command += str(batt4_stats[j]) + "','"
        
        for i in range (0,96):
                command += str(cell_IRs[i]) + "','"
                
        command = command[:-2] + ");"
        curs.execute(command)
        
        return "success"

#record messages
conn = sqlite3.connect(db_path)
curs = conn.cursor()

if (os.path.exists(db_path)):
        
        curs.execute("SELECT date, time FROM IR LIMIT 1")
        data = curs.fetchall()
        
        if (len(data) > 0): #database not empty
                datumDate = data[0][0].strip()
                datumTime = data[0][1].strip()
                
                #check time, if less than 1 minute ago, good
                p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True) 
                (output, err) = p.communicate()
                current_date = output     

                if (datumDate != current_date[:10] or (datumTime != current_date[11:16])):
                        print update_database()
                else:
                        print "success"
        else:
                #there are no entries in the database
                print update_database()
    
else:
	curs.execute("""CREATE TABLE IR(date DATE, time TIME, packVoltage REAL, packSOC INTEGER, totalCycles INTEGER, 
		battHighTemp REAL, battLowTemp REAL, battHighTempId INTEGER, battLowTempId INTEGER,
        IR1Avg REAL, IR1High REAL, IR1Low REAL,
        IR2Avg REAL, IR2High REAL, IR2Low REAL, 
        IR3Avg REAL, IR3High REAL, IR3Low REAL,
        IR4Avg REAL, IR4High REAL, IR4Low REAL, 
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

        #get current date & time
        p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True) 
        (output, err) = p.communicate()
        current_date = output

	#Fill it with stuff!
	print update_database()

conn.commit()
conn.close()