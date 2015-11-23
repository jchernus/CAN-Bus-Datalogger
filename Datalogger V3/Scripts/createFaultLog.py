#!/usr/bin/env python

import sqlite3, subprocess, re

csv_path = "/var/tmp/logs/FaultLog.csv"
db_path = "/data/databases/FaultDictionary.db"

conn = sqlite3.connect(db_path)
curs = conn.cursor()
 
#note time
p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
current_date = output 

with open(csv_path, 'w+') as file:
        file.write("Date:," + current_date[:10] + "\n")
        file.write("Time:," + current_date[11:] + "\n\n")

        #SEVCON Fault Retreival
        file.write('Fault ID, Hours Ago [h], Minutes & Seconds Ago\n')
        
        for num in range(0,40):
                #select event through 4111
                p = subprocess.Popen("cansend can0 601#2B114100" + hex(num)[2:].zfill(2) + "00EFFA) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)

                #send request for event ID through 4112
                p = subprocess.Popen("(sleep 0.05; cansend can0 601#4012410100000000; cansend can0 601#4012410200000000; cansend can0 601#4012410300000000;) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                p = subprocess.Popen("candump -t A -n 3 -T 50 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()

                if len(output) > 0:  # got the response message

                        if ("581  [8] 4F 12 41 01 00 00 00 00" in output):                      #single message
                                #parse CAN data
                                try:
                                        lines = output.split("\n").strip()
                                        
                                        data = lines[0].split("  ")[3][16:21].strip()
                                        faultID = data[3:] + data[:2]

                                        hours = lines[1].split("  ")[3][].strip()

                                        minutes = lines[2].split("  ")[3][].strip()
                                except:
                                        return "Error: Unable to parse data. Data: " + faultData

                                #query database for fault description and remedy
                                curs.execute("SELECT * FROM FaultDictionary LIMIT 1 WHERE faultID = '" + int(faultID, 16) + "'")   #faultID, message, description, action
                                data = curs.fetch()

                                #record to csv
                                file.write(hours + "," + minutes + "," + data[0] + "," + data[1] + "," + data[2] + "," + data[3] + "\n")

                        elif ("581  [8] 80" in output):                                         #crashed
                                return "Error: crashed motor controller. Please do a key cycle to recover, and then try again."
                        else:
                                return "Error: Unexpected message format, cannot decode reply from motor controller."
                else:
                        return "Error: Did not receive reply from motor controller."

        #BMS Fault Retreival
        file.write('Fault ID\n')

        

conn.close()
