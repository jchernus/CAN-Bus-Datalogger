#!/usr/bin/env python

import subprocess, os

path="/data/scripts/"
filename = "daylightSavingsDates.txt"
    
#check the date, set the filename
p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
today = output.strip() + "\n"

#open file with all of the dates
datesFile = open(path + filename, 'r+')
dates = datesFile.readlines()

#check if today is a daylight savings date
for date in dates:
    if today == date:
        if date[5:7] == "11":
            #set time back an hour
            command = "sudo date -s \"-1 hour\""
        elif date[5:7] == "03":
            #set time forward an hour
            command = "sudo date -s \"+1 hour\""
            
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        #also update the RTC
        p = subprocess.Popen("sudo hwclock -w", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        break

#try to remove today's date from the list
if today in dates:
    dates.remove(today)

#write the remaining dates back to the file
datesFile.close()
datesFile = open(path + filename, 'w+')

for date in dates:
    datesFile.write(date)
datesFile.close()

