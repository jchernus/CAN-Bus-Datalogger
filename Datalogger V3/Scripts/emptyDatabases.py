import sys, sqlite3

path = "/data/databases/"

dbname = "Logs.db"

#create database 
conn=sqlite3.connect(path + dbname)
curs=conn.cursor()

curs.execute("""DELETE FROM dailylogs;""")
curs.execute("""DELETE FROM summary;""")
curs.execute("""DELETE FROM days;""")
curs.execute("""VACUUM;""")

conn.commit()
