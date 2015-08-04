#!/usr/bin/env python

import sqlite3, os

db_path = "/data/databases/Logs.db"
csv_path = "/var/tmp/summary/Summary.csv"

if (os.path.exists(db_path)):
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        with open(csv_path, 'w+') as file:
                file.write("Date, Odometer [km], Battery Energy Out (Operating) [kWh], Battery Energy In (Charging) [kWh], Hours Charging [h], Hours Operating [h], Hours Running [h]\n")
                for row in curs.execute("SELECT * FROM summary ORDER BY date"):
                        str_row = ' '.join([str(line).strip() + "," for line in row]).strip() + "\n"
                        file.write(str_row)

        conn.close()
        print "Success"
else:
        #How to say that things failed?
        raise IOError('Database file does not exist.')
