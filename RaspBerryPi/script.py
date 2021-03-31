import requests
import glob
import os
import sys

listFiles = glob.glob("*.jpg")
listFiles.extend(glob.glob("*.jpeg"))
listFiles.extend(glob.glob("*.png"))
lastFile = max(listFiles, key = os.path.getctime)
print(lastFile)

url = 'http://tatacoaastronomia.com/obtener-imagen.php'
files = {'file': open(lastFile, 'rb')}
r = requests.post(url, files = files)