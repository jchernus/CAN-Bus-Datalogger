import sys, sqlite3

db_path = "/data/databases/Logs.db"

dates = sys.argv[1:]

#create database 
conn=sqlite3.connect(db_path)
curs=conn.cursor()

for date in dates:
    curs.execute("DELETE FROM dailylogs WHERE date = '" + date + "';")
    curs.execute("DELETE FROM days WHERE date = '" + date + "';")
    curs.execute("VACUUM;")

conn.commit()
print "success"
