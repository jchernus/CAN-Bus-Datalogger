#!/usr/bin/env python

import sqlite3, os

db_path = "/data/databases/Logs.db"

if (os.path.exists(db_path)):
        logsDB = sqlite3.connect(db_path)
        logsCurs = logsDB.cursor()

        output = "True"
        while (output == "True"):
                p = subprocess.Popen("$(df -P $FILESYSTEM | awk '{ gsub(\"%\",\"\"); capacity = $5 }; END { print capacity }') -gt 95", cwd="/data/can-test_pi2/", stdout=subprocess.PIPE, shell=True)
                (output, err) = p.communicate()
                print output #should be TRUE or FALSE

                #Clean out daily logs
                logsCurs.execute("SELECT date FROM dailyLogs ORDER BY date LIMIT 1") #get oldest date
                date = logsCurs.fetchone()[0]
                logsCurs.execute("DELETE FROM dailyLogs WHERE date = " + date)

                #Clean out fault logs
                logsCurs.execute("SELECT date FROM faultLogs ORDER BY date LIMIT 1") #get oldest date
                date = logsCurs.fetchone()[0]
                logsCurs.execute("DELETE FROM faultLogs WHERE date = " + date)
                
                logsDB.commit()
        logsDB.close()
        print "Success"
else:
        #How to say that things failed?
        raise IOError('Database file does not exist.')
