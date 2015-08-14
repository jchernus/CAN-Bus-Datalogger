#!/usr/bin/env python

import sqlite3, os

db_path = "/data/databases/Logs.db"
csv_path = "/var/tmp/logs/"

if (os.path.exists(db_path)):

        #Connect to Database
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        #Create needed folder structure
	if not (os.path.exists(csv_path)):
                os.makedirs(csv_path)

	#Create fault log file
        with open(csv_path + "FaultLog.csv", 'w+') as file:
                file.write("Date, Time, Fault ID\n")
                for row in curs.execute("SELECT faultLogs.date, faultLogs.time, faultLogs.id, FaultDictionary.description FROM faultLogs INNER JOIN FaultDictionary ON faultLogs.id = FaultDictionary.id ORDER BY date, time;"):
                        str_row = ' '.join([str(line).strip() + "," for line in row]).strip() + "\n"
                        print str_row
                        file.write(str_row)

        conn.close()
        print "Success"
else:
        #How to say that things failed?
        raise IOError('Database file does not exist.')
