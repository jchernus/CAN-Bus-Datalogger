import subprocess, os, time

path = "/var/tmp/"
path2 = "/data/dailylogs/"
filename = "testlog0000.txt"

count = 0
while (True):
    p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    logFile = open(path + filename, 'a+')
    logFile.write(output.strip())
    time.sleep(1)
    count += 1
    logFile.close()
    if count == 30: #after 30 seconds move the file to the non-ram drive
        os.rename(path + filename, path2 + filename)
        filename = filename[:-8] + str(int(filename[-8:-4])+1) + filename[-4:]
        count = 0
