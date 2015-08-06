#!/usr/bin/env python

import sqlite3, os

db_path = "/data/databases/Logs.db"
csv_path = "/var/tmp/summary/"

if (os.path.exists(db_path)):

        #Connect to Database        
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        #Create needed folder structure
	if not (os.path.exists(csv_path)):
                os.makedirs(csv_path)

        #Create summary fily
        with open(csv_path + "Summary.csv", 'w+') as file:
                file.write("Date, Odometer [km], Battery Energy Out (Operating) [kWh], Battery Energy In (Charging) [kWh], Hours Charging [h], Hours Operating [h], Hours Running [h]\n")
                for row in curs.execute("SELECT * FROM summary ORDER BY date"):
                        str_row = ' '.join([str(line).strip() + "," for line in row]).strip() + "\n"
                        file.write(str_row)

        conn.close()
        print "Success"
else:
        #How to say that things failed?
        raise IOError('Database file does not exist.')
