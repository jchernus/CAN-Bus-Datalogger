#!/usr/bin/env python

import sqlite3, os

db_path = "/data/databases/Logs.db"
csv_path = "/var/tmp/logs/FaultLog.csv"

if (os.path.exists(db_path)):
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        with open(csv_path, 'w+') as file:
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
