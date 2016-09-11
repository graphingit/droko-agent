#!/usr/bin/env __PYTHONVER__

import psutil
import time
import sys

if __name__ == "__main__":
    
    # Output needs to be in comma format, eg:
    # epoch,checkname,value,metadata
    # Eg:
    # 1430157905,os.process.count./,64.7,metric=percent;title=/
    # 1430157905,os.process.count./home,91.4,metric=percent;title=/home
    # 1430157905,os.process.count./boot,34.8,metric=percent;title=/boot
            

    # We need to determine which version of psutil we are running
    psutilversion = 3
    try:
        pids = psutil.pids()   # version 3.x
        psutilversion = 3
    except:
        pass

    try:
        pids = psutil.get_pid_list()   # version 1.x and 2.x
        psutilversion = 2
    except:
        pass

    # Main loop
    while True:
        # Get the current unix epoch time
        now = str(int(time.time() / 1))

        running = 0
        sleeping = 0
        zombie = 0
        disksleep = 0 
        dead = 0
        idle = 0
        locked = 0
        waiting = 0
        total = 0

        
        if psutilversion == 3:
            pids = psutil.pids()   # version 3.x
            total = len(pids)
            for pid in pids:
                try:
                    p = psutil.Process(pid)
                    status = p.status()

                    if status == 'running':
                        running += 1
                    if status == 'sleeping':
                        sleeping += 1
                    if status == 'zombie':
                        zombie += 1
                    if status == 'disk-sleep':
                        disksleep += 1
                    if status == 'dead':
                        dead += 1
                    if status == 'idle':
                        idle += 1
                    if status == 'locked':
                        locked += 1
                    if status == 'waiting':
                        waiting += 1
                except psutil.NoSuchProcess:
                    pass  
        
        if psutilversion == 2:
            pids = psutil.get_pid_list()   # version 1.x and 2.x
            total = len(pids)
#            for pid in psutil.process_iter():
            for pid in pids:
                try:
                    p = psutil.Process(pid)
                
                    #_status = pid.as_dict(['status'])
                    _status = p.as_dict(['status'])
                    status = _status['status']

                    if status == 'running':
                        running += 1
                    if status == 'sleeping':
                        sleeping += 1
                    if status == 'zombie':
                        zombie += 1
                    if status == 'disk-sleep':
                        disksleep += 1
                    if status == 'dead':
                        dead += 1
                    if status == 'idle':
                        idle += 1
                    if status == 'locked':
                        locked += 1
                    if status == 'waiting':
                        waiting += 1
                except psutil.NoSuchProcess:
                    pass  

  
        print(now + ",os.processes.count.total"     + "," + str(total)     + ",title=total")
        print(now + ",os.processes.count.running"   + "," + str(running)   + ",title=running")
        print(now + ",os.processes.count.sleeping"  + "," + str(sleeping)  + ",title=sleeping")
        print(now + ",os.processes.count.zombie"    + "," + str(zombie)    + ",title=zombie")
        print(now + ",os.processes.count.idle"      + "," + str(idle)      + ",title=idle")
 
        sys.stdout.flush()
        time.sleep(1)
