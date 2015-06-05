#!/usr/bin/env python

import subprocess, sqlite3

#Check the date, set the filename
p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
conn=sqlite3.connect(output.strip() + ".db")

curs=conn.cursor()
#curs.execute("CREATE TABLE temps (tdate DATE, ttime TIME, zone TEXT, temperature NUMERIC)")
curs.execute("INSERT INTO temps values(date('now'), time('now'), 'Saskatoon', '20')")
conn.commit()

for row in curs.execute("SELECT * FROM temps"):
        print row

conn.close()
