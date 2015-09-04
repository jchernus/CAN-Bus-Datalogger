#!/usr/bin/env python

import sqlite3, os, subprocess

db_path = "/data/databases/Logs.db"

if (os.path.exists(db_path)):
        logsDB = sqlite3.connect(db_path)
        logsCurs = logsDB.cursor()

        p = subprocess.Popen("df -P $FILESYSTEM | awk '/root/' | awk '{ gsub(\"%\",\"\"); capacity = $5 }; END { print capacity }'", cwd="/data/", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        print output
        
        while (int(output) > 95):
		try:
		        #Clean out daily logs
		        logsCurs.execute("SELECT date FROM dailyLogs ORDER BY date LIMIT 1;") #get oldest date
		        date = logsCurs.fetchone()[0]
		        logsCurs.execute("DELETE FROM dailyLogs WHERE date = '%s';" % date)
		        logsCurs.execute("VACUUM;")

		        #Clean out fault logs (FUTURE DEVELOPMENT)
		        #logsCurs.execute("SELECT date FROM faultLogs ORDER BY date LIMIT 1;") #get oldest date
		        #date = logsCurs.fetchone()[0]
		        #logsCurs.execute("DELETE FROM faultLogs WHERE date = '%s';" % date)
		        
		        logsDB.commit()

		        p = subprocess.Popen("df -P $FILESYSTEM | awk '/root/' | awk '{ gsub(\"%\",\"\"); capacity = $5 }; END { print capacity }'", cwd="/data/", stdout=subprocess.PIPE, shell=True)
		        (output, err) = p.communicate()
                	print output
		except:
			print "We have a problem, Houston! We're out of space."
			break
                
        logsDB.close()
        print "Success"
else:
        #How to say that things failed?
        raise IOError('Database file does not exist.')
