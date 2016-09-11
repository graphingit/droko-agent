#!/usr/bin/env __PYTHONVER__

import psutil
import time
import sys

if __name__ == "__main__":
    
    # Output needs to be in comma format, eg:
    # epoch,checkname,value,metadata
    # Eg:
    # 1430157905,os.disk.partition./,64.7,metric=percent;title=/
    # 1430157905,os.disk.partition./home,91.4,metric=percent;title=/home
    # 1430157905,os.disk.partition./boot,34.8,metric=percent;title=/boot

    # list of devices or mountpoints we don't want to track
    filterdisk = [ 'loop' ]

    while True:
        try:
            # Get the current unix epoch time
            now = str(int(time.time() / 1))

            partitions = psutil.disk_partitions()
            for key in partitions:
                (device, mountpoint, fstype, opts) = key
                partname = str(device.rsplit('/',1)[1]) 

                # Skip if the source location has '/media' or 'loop' in it. We don't care about these devices or mountpoints
                if any(substring in partname for substring in filterdisk):
                    continue
                if any(substring in mountpoint for substring in filterdisk):
                    continue 

                # Get the usage % of each partition
                (total, used, free, percent) = psutil.disk_usage(mountpoint)

                print(now + ",os.disk.partition." + mountpoint.replace('.','') + "," + str(percent) + ",metric=percent;y_max=auto;title=" + mountpoint)
   
            sys.stdout.flush()
            time.sleep(1)
        except:
            pass
    
