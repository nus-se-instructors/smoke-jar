import csv
import os, sys
import shutil
import subprocess
import time

JAVA_PATH = "java"

table = []

for root, dirs, files in os.walk("jars"):
    for jarname in files:
        if jarname.endswith(".jar"):    #confirm
            print(jarname)
            jarpath = os.path.join(root, jarname)
            if not os.path.exists("jar_test"):
                os.makedirs("jar_test")
            shutil.copy2(jarpath,"jar_test")
            os.chdir("jar_test")
            isOk = False
            jarproc = subprocess.Popen([JAVA_PATH, "-jar", jarname],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=False)
            try:
                poll = jarproc.wait(2.2)
            except subprocess.TimeoutExpired:
                print("Ok")
                isOk = True
            os.popen('TASKKILL /PID java.exe /F')
            if isOk:
                err = ""
            else:
                #rerun and log the error
                jarproc = subprocess.Popen([JAVA_PATH, "-jar", jarname],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=False)
                err = jarproc.communicate()[1]
                os.popen('TASKKILL /PID java.exe /F')  #shouldn't be necessary
            table.append([str(jarname), str(err)])
            os.chdir("..")
            time.sleep(1)
            shutil.rmtree("jar_test")

with open("windows.csv","w",newline="") as f:
    writer = csv.writer(f)
    writer.writerows([["JAR","error"]])
    writer.writerows(table)