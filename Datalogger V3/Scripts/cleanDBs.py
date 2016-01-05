#!/usr/bin/env python

import sqlite3, os, subprocess

db_paths = ["/data/databases/Logs.db"]

for db_path in db_paths:
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
                                logsCurs.execute("DELETE FROM days WHERE date = '%s';" % date)
                                logsCurs.execute("VACUUM;")

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
