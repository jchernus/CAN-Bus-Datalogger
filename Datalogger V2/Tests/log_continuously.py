import subprocess, os, time

path = "/data/dailylogs/continuous/"
filename = "testlog.txt"

while (True):
    p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    logFile = open(path + filename, 'a+')
    logFile.write(output.strip())
    time.sleep(1)
    logFile.close()
