import os, sys

dictionary = {}
for file in os.listdir("\data\RAW"):
    if file.endswith(".log"):
        hour = int(file[19:-8])
        minute = int(file[21:-6])
        try:
            dictionary[hour] += 1
        except:
            dictionary[hour] = 1
        #print str(hour) + " : " + str(minute)

print "\n\n"
for item in dictionary:
    print str(item) + ": " + str(dictionary[item])
