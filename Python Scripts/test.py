import os
try:
    os.rename("2.txt", "3.txt")
except:
    os.remove("2.txt")
    
