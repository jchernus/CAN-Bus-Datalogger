#!/usr/bin/env python

import sqlite3, subprocess, re

db_path = "/data/databases/Live.db"

faultList = []

def parse_data(faultData):
        global faultList
        
        #remove whitespaces entirely
        pattern = re.compile(r'\s+')
        faultData = re.sub(pattern, '', faultData)

        for x in range (0, len(faultData), 4):
                id = faultData[x] + faultData[x+1] + faultData[x+2] + faultData[x+3]
                if not id == "0000":
                        faultList.append(id)         

def update_database():
        faultData = ""

        #send request for BMS faults
        p = subprocess.Popen("(sleep 0.1; cansend can0 7E3#0103000000000000) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)

        #receive reply
        p = subprocess.Popen("candump -t A -n 1 -T 500 can0,7EB:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        if len(output) > 0:  # got the response message

                if ("7EB   [8]  02 43" in output):                #single message
                        
                        #no faults present
                        pass

                elif ("7EB   [8]  04 43" in output):                #single message
                        
                        faultData = output.strip().split("  ")[4][9:14].strip()
                        
                elif ("7EB   [8]  10 " in output):           #more messages available
        
                        faultData = output.strip().split("  ")[4][12:].strip()

                        msgCount = int(output.strip().split("  ")[4][9:11],16)
                                
                        #send request for more data
                        p = subprocess.Popen("(sleep 0.1; cansend can0 7E3#30) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)

                        #receive remaining messages
                        p = subprocess.Popen("candump -t A -n " + str(msgCount) + " -T 200 can0,7EB:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                        (output, err) = p.communicate()

                        if len(output) > 0:                     # got the response message
                
                                lines = output.strip().split("\n")
                                for line in lines:
                                        try:
                                                data = line.strip().split("  ")
                                                faultData = faultData + data[4].strip()[2:]  
                                        except:
                                                return "Error: Unable to parse line. Line: " + line

                        else:
                                return "Error: Did not receive additional messages from BMS."
                else:
                        return "Error: Unexpected message format, cannot decode reply from BMS. Output: " + output
        else:
                return "Error: Did not receive reply from BMS."

        #parse the data

        if faultData != "":
                try:
                        parse_data(faultData)
                except:
                        return "Error: Trouble parsing data."

        #Request faults from Mr. Sevcon
        p = subprocess.Popen("(sleep 0.1; cansend can0 601#4000530100000000;) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
        p = subprocess.Popen("candump -t A -n 1 -T 500 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)

        (output, err) = p.communicate()

        if len(output) > 0:  # got the response message

                if ("581   [8]  4B 00 53 01" in output):                      #single message
                        #parse CAN data
                        numFaults = 0
                        try:
                                numFaults = int(output.split("  ")[4][12:14].strip(), 16)
                        except:
                                return "Error: Unable to parse number of faults. Data: " + faultData

                        for index in range (0, numFaults):
                                #select message
                                p = subprocess.Popen("(sleep 0.1; cansend can0 601#2B005302" + hex(index)[2:].zfill(2) + "00EFFA;) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                                p = subprocess.Popen("candump -t A -n 1 -T 150 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)                                
                                (output, err) = p.communicate()

                                #ask for & read message
                                p = subprocess.Popen("(sleep 0.1; cansend can0 601#4000530300000000;) &", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                                p = subprocess.Popen("candump -t A -n 1 -T 150 can0,581:7ff", cwd="/data/can-utils/", stdout=subprocess.PIPE, shell=True)
                                (output, err) = p.communicate()
                                
                                #parse messages
                                if len(output) > 0:  # got the response message
                                        lines = output.strip().split("\n")
                                        
                                        for line in lines:
                                                if ("581   [8]  4B 00 53 03" in line):                      #single message
                                                        try:
                                                                data = line.split("  ")[4][12:17].strip()
                                                                faultList.append(int(data[3:] + data[:2], 16))
                                                        except:
                                                                return "Error: Unable to parse fault data. Data: " + data
                                                        
                                                elif ("581   [8]  80" in output):                           #crashed
                                                        return "Error: Crashed motor controller. Please do a key cycle to recover, and then try again."

                elif ("581   [8]  80" in output):                                                           #crashed
                        return "Error: Crashed motor controller. Please do a key cycle to recover, and then try again."
                else:
                        return "Error: Unexpected message format, cannot decode reply from motor controller."
        else:
                return "Error: Did not receive reply from motor controller."

        #Write to database
        curs.execute("DELETE FROM faults;")
        curs.execute("VACUUM;")

        #print faults
        for fault in faultList:
                command = "INSERT INTO faults VALUES('" + current_date[:11] + "','" + str(fault) + "');"
                curs.execute(command)
        
        return "success"

#note time
p = subprocess.Popen("date +\"%Y-%m-%d %H:%M\"", stdout=subprocess.PIPE, shell=True) 
(output, err) = p.communicate()
current_date = output 

#record messages
conn = sqlite3.connect(db_path)
curs = conn.cursor()

tableExists = False
try:
        curs.execute("SELECT date FROM faults LIMIT 1")
        tableExists = True
except:
        pass

if (not tableExists):
        curs.execute("""CREATE TABLE faults(date DATE, faultID INTEGER)""")
        conn.commit()

print update_database()
#print "success"

conn.commit()
conn.close()
