#!/usr/bin/env python

import sqlite3, subprocess, re, os

csv_path = "/var/tmp/logs/"
db_path = "/data/databases/FaultDictionary.db"

conn = sqlite3.connect(db_path)
curs = conn.cursor()
 
#note time
p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
current_date = output

#Create needed folder structure
if not (os.path.exists(csv_path)):
        os.makedirs(csv_path)

csv_path += "FaultLog.csv"

with open(csv_path, 'a+') as file:
        file.write("Date:," + current_date[:10] + "\n")
        file.write("Time:," + current_date[11:] + "\n\n")

        #SEVCON Fault Retreival
        file.write('Fault ID, Hours Ago [h], Minutes & Seconds Ago\n')
        
        for num in range(0,40):
                #select event through 4111
                p = subprocess.Popen("cansend can0 601#2B114100" + hex(num)[2:].zfill(2) + "00EFFA", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                p = subprocess.Popen("candump -t A -n 1 -T 100 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()
                
                #send request for event ID through 4112
                p = subprocess.Popen("(sleep 0.1; cansend can0 601#4012410100000000; cansend can0 601#4012410200000000; cansend can0 601#4012410300000000;) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                p = subprocess.Popen("candump -t A -n 3 -T 500 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()

                if len(output) > 0:  # got the response message

                        lines = output.split("\n").strip()

                        for line in lines:
                                if ("581   [8]  4F 12 41 01" in line):                      #single message
                                        #parse CAN data
                                        try:
                                                data = lines[0].split("  ")[3][16:21].strip()
                                                faultID = int(data[3:] + data[:2], 16)
                                        except:
                                                print "Error: Unable to parse data. Data: " + faultData
                                        
                                if ("581   [8]  4F 12 41 02" in line):                      #single message
                                        #parse CAN data
                                        try:
                                                data = lines[0].split("  ")[3][16:21].strip()
                                                hours = int(data[3:] + data[:2], 16)
                                        except:
                                                print "Error: Unable to parse data. Data: " + faultData
                                        
                                if ("581   [8]  4F 12 41 03" in line):                      #single message
                                        #parse CAN data
                                        try:
                                                minutes = int(lines[0].split("  ")[3][16:18].strip(), 16)
                                        except:
                                                print "Error: Unable to parse data. Data: " + faultData

                                elif ("581   [8]  80" in output):                                         #crashed
                                        print "Error: Crashed motor controller. Please do a key cycle to recover, and then try again."
                                else:
                                        print "Error: Unexpected message format, cannot decode reply from motor controller."

                        #query database for fault description and remedy
                        curs.execute("SELECT * FROM FaultDictionary LIMIT 1 WHERE faultID = '" + int(faultID, 16) + "'")   #faultID, message, description, action
                        data = curs.fetch()

                        #record to csv
                        file.write(hours + "," + minutes + "," + data[0] + "," + data[1] + "," + data[2] + "," + data[3] + "\n")

                else:
                        print "Error: Did not receive reply from motor controller."

        #BMS Fault Retrieval
        file.write('Fault ID\n')

conn.close()
