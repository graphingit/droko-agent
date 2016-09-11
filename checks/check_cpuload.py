#!/usr/bin/env __PYTHONVER__

import os
import time
import sys

if __name__ == "__main__":
    while True:
        try:
            # Get the current unix epoch time
            now = str(int(time.time() / 1))
    
            # Output needs to be in comma format, eg:
            # epoch,checkname,value,metadata
            # Eg:
            # 1425057446,os.cpu.load.load1,0.56,title=load1
            # 1425057446,os.cpu.load.load5,0.23,title=load5
            # 1425057446,os.cpu.load.load15,0.11,title=load15

            load = os.getloadavg()
            result = "%s %s %s" % load
            loadstring = result.split()

            print(now + ",os.cpu.load.load1,"  + loadstring[0] + ",title=load1")
            print(now + ",os.cpu.load.load5,"  + loadstring[1] + ",title=load5")
            print(now + ",os.cpu.load.load15," + loadstring[2] + ",title=load15")

            sys.stdout.flush()
            time.sleep(1)
        except:
            pass
   

