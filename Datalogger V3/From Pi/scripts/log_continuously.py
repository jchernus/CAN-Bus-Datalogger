import subprocess, os, time

path = "/data/dailylogs/continuous/"
filename = "testlog.txt"

while (True):
    p = subprocess.Popen("date +\"%Y-%m-%d %H:%M:%S\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    logFile = open(path + filename, 'a+')
    logFile.write(output)
    time.sleep(1)
    logFile.close()
