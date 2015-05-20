import subprocess, os, time

path2 = "/data/dailylogs/continuous/"
filename = "testlog.txt"

while (True):
    p = subprocess.Popen("date +\"%F\"", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    logFile = open(path + filename, 'w+')
    logFile.write(output.strip())
    time.sleep(1)
    logFile.close()
