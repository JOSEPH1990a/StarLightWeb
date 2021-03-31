import subprocess
import time
for i in range(0,100000):
    subprocess.Popen(["nohup","python3","script.py"])
    time.sleep(5)