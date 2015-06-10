import subprocess, os, re, sqlite3

previous_date = ""
previous_time = 0

counter = 0

temppath = "/var/tmp/logs/"
permpath = "/data/databases/"

#Create the paths that are needed to store files
if (not os.path.exists(temppath)):
    os.mkdir(temppath)

if (not os.path.exists(permpath)):
    os.mkdir(permpath)

while (True): #Checks the date, starts logging, when the logging ends (end of day, or end of time-period) it will transfer data to permanent location.

    #check the date, set the filename
    p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    filename = output.strip() + ".db"

    #remove file if already exists due to crashed code
    if (os.path.exists(temppath + filename)):
        os.remove(temppath + filename)

    #create database 
    conn=sqlite3.connect(temppath + filename)
    curs=conn.cursor()
    curs.execute("CREATE TABLE log (time TEXT)")
    conn.commit()
    conn.close()
            
    while(True): #Logging, a change of date or 120 seconds will break out of this loop
        
        #get date & time
	p = subprocess.Popen("date +\"%Y-%m-%d %H:%M:%S\"", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        current_date = output

        #if new date, break
        if (previous_date != "" and current_date[:10] != previous_date[:10]):
            previous_date = current_date #DID I PUT THIS IN HERE?
            break     #this will exit this while loop and return to the parent one, creating a new file (with the new date)
        
        #calculate time difference between current and previous time stamps
        times = str(current_date[11:19]).split(":")
        current_time = int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2]) #convert to seconds
        time_span = 1 #if there is no previous time stamp, assume 1s
        if previous_time is not None:
            time_span = (current_time - previous_time)
            if time_span > 2: #if time between time stamps is too long, assume 1s
                time_span = 1
        previous_time = current_time
        previous_date = current_date
            
        #if less than a second
        if time_span >= 1:
            
            #write values to excel
            conn=sqlite3.connect(temppath + filename)
	    curs=conn.cursor()

            curs.execute("INSERT INTO log values('" + str(current_date) + "')")
	    conn.commit()
	    conn.close()
    
            counter += 1

            if counter == 20:
                counter = 0
                #time to move this data to a permanent location and start a new temporary file
                break

    #Must be done parsing either 2 minutes worth of data, or the end of the day's data,
    #move data to permanent location:
	
    createPermDBFile = False
    if (not os.path.exists(permpath + filename)):
        createPermDBFile = True
    
    #append the log data
    permConn=sqlite3.connect(permpath + filename)
    permCurs=permConn.cursor()
	
    if (createPermDBFile):
        permCurs.execute("CREATE TABLE log (time TEXT)")
    
    tempConn=sqlite3.connect(temppath + filename)
    tempCurs=tempConn.cursor()
            
    for row in tempCurs.execute("SELECT * FROM log"):
        line = "INSERT INTO log values('"
        for item in row:
            line += str(item).strip()
        line += "')"
        print line
        permCurs.execute(line)
    permConn.commit()
    permConn.close()
    
    tempConn.close()

    #delete the temporary file
    os.remove(temppath + filename)
