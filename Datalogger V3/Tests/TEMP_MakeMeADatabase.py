#!/usr/bin/env python

import sqlite3, os, random

db_path = "/data/databases/Battery.db"

conn = sqlite3.connect(db_path)
curs = conn.cursor()
        
##curs.execute("""CREATE TABLE battery(date DATE, time TIME, packVoltage REAL, packSOC INTEGER, 
##batt1Avg REAL, batt1High REAL, batt1Low REAL, batt1Temp REAL, 
##batt2Avg REAL, batt2High REAL, batt2Low REAL, batt2Temp REAL, 
##batt3Avg REAL, batt3High REAL, batt3Low REAL, batt3Temp REAL, 
##batt4Avg REAL, batt4High REAL, batt4Low REAL, batt4Temp REAL, 
##cell1 REAL, cell2 REAL, cell3 REAL, cell4 REAL, cell5 REAL, cell6 REAL, cell7 REAL, cell8 REAL, cell9 REAL, cell10 REAL, cell11 REAL, cell12 REAL,
##cell13 REAL, cell14 REAL, cell15 REAL, cell16 REAL, cell17 REAL, cell18 REAL, cell19 REAL, cell20 REAL, cell21 REAL, cell22 REAL, cell23 REAL, cell24 REAL,
##cell25 REAL, cell26 REAL, cell27 REAL, cell28 REAL, cell29 REAL, cell30 REAL, cell31 REAL, cell32 REAL, cell33 REAL, cell34 REAL, cell35 REAL, cell36 REAL,
##cell37 REAL, cell38 REAL, cell39 REAL, cell40 REAL, cell41 REAL, cell42 REAL, cell43 REAL, cell44 REAL, cell45 REAL, cell46 REAL, cell47 REAL, cell48 REAL,
##cell49 REAL, cell50 REAL, cell51 REAL, cell52 REAL, cell53 REAL, cell54 REAL, cell55 REAL, cell56 REAL, cell57 REAL, cell58 REAL, cell59 REAL, cell60 REAL,
##cell61 REAL, cell62 REAL, cell63 REAL, cell64 REAL, cell65 REAL, cell66 REAL, cell67 REAL, cell68 REAL, cell69 REAL, cell70 REAL, cell71 REAL, cell72 REAL,
##cell73 REAL, cell74 REAL, cell75 REAL, cell76 REAL, cell77 REAL, cell78 REAL, cell79 REAL, cell80 REAL, cell81 REAL, cell82 REAL, cell83 REAL, cell84 REAL,
##cell85 REAL, cell86 REAL, cell87 REAL, cell88 REAL, cell89 REAL, cell90 REAL, cell91 REAL, cell92 REAL, cell93 REAL, cell94 REAL, cell95 REAL, cell96 REAL		
##)""")

row = """INSERT INTO battery VALUES(
'2015-08-05', '10:47', 320, 90,
3.41, 3.64, 3.1, 21,
3.42, 3.63, 3.2, 22,
3.43, 3.62, 3.3, 23,
3.44, 3.61, 3.4, 24,"""

for x in range (0,96):
        row = row + str(random.randrange(208, 365, 5)/100.0) + ", "

row = row[:-2] + ")"

curs.execute(row)

conn.commit()
conn.close()
print "Success"
