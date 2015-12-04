#!/usr/bin/env python

import sqlite3, subprocess, re, os

faultID = hours = minutes = 0

csv_path = "/var/tmp/logs/"
db_path = "/data/databases/FaultDictionary.db"

def parse_msg (line):
        
        global faultID, hours, minutes
        
        if (" 12 41 01 " in line):                        #single message
                #parse CAN data
                try:
                        data = line.split("  ")[4][12:17].replace(" ","")
                        faultID = int(data[2:] + data[:2], 16)
                except:
                        return "Error: Unable to parse data. Data: " + line
                
        elif (" 12 41 02 " in line):                      #single message
                #parse CAN data
                try:
                        data = line.split("  ")[4][12:17].replace(" ","")
                        hours = int(data[2:] + data[:2], 16)
                except:
                        return "Error: Unable to parse data. Data: " + line
                
        elif (" 12 41 03 " in line):                      #single message
                #parse CAN data
                try:
                        minutes = int(line.split("  ")[4][12:14], 16)
                except:
                        return "Error: Unable to parse data. Data: " + line

        elif ("581   [8]  80" in line):                           #crashed
                return "Error: Crashed motor controller. Please try again."
        else:
                return "Error: Unexpected message format, cannot decode reply from motor controller. Data: " + line

        return ""

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

with open(csv_path, 'w+') as file:
        file.write("Date:," + current_date[:10] + "\n")
        file.write("Time:," + current_date[11:] + "\n\n")

        #SEVCON Fault Retreival
        file.write('Hours Ago [h], Minutes & Seconds Ago, Fault ID, Fault Name, Fault Cause, Fault Remedy\n')
        
        #send password to gain access
        p = subprocess.Popen("cansend can0 601#2B005002DF4BEFFA", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
        p = subprocess.Popen("candump -t A -n 1 -T 100 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        
        for num in range(0,40):
              
                #select event through 4111
                p = subprocess.Popen("cansend can0 601#2B114100" + hex(num)[2:].zfill(2) + "00EFFA", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                p = subprocess.Popen("candump -t A -n 1 -T 100 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()
                
                #send request for event ID through 4112
                p = subprocess.Popen("(sleep 0.1; cansend can0 601#4012410100000000; cansend can0 601#4012410200000000; cansend can0 601#4012410300000000;) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                p = subprocess.Popen("candump -t A -n 3 -T 500 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()

                message = ""
                if len(output) > 0:  # got the response message

                        lines = output.strip().split("\n")

                        for line in lines:
                                message = parse_msg(line)

                else:
                        message = "Error: Did not receive reply from motor controller."
                
                if message == "":      
                        #query database for fault description and remedy
                        curs.execute("SELECT * FROM FaultDictionary WHERE faultID = '" + str(faultID) + "'")   #faultID, message, description, action
                        for row in curs: #only ever one, since unique
                                #record to csv
                                file.write(str(hours) + "," + str(minutes) + "," + str(row[0]) + "," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "\n")
                                #print str(hours) + "," + str(minutes) + "," + str(row[0]) + "," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "\n"
                else:
                        print message
                        break

        #BMS Fault Retrieval
        #file.write('\n\nFault ID\n')

if not message == "":
        os.remove(csv_path)
        
conn.close()
