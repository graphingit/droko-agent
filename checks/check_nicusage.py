#!/usr/bin/env __PYTHONVER__

import psutil
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
            # 1430157858,os.nic.bytes.wlan0_out,32863319809,metric=bps;title=wlan0_out
            # 1430157858,os.nic.bytes.wlan0_in,6320095757,metric=bps;title=wlan0_in
            # 1430157858,os.nic.bytes.em1_out,4128073428,metric=bps;title=em1_out
            # 1430157858,os.nic.bytes.em1_in,3156351939,metric=bps;title=em1_in

            # List of network devices we want to exclude
            filternics = ['lo']

            nics = psutil.net_io_counters(pernic=True)
   
            for nic in nics:
                (bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout) = nics[nic]

                if nic not in filternics:
                    # Ignore inactive network interfaces
                    if packets_recv != 0 and packets_sent != 0:
                        print(now + ",os.nic.bytes." + nic + "_out," + str(bytes_sent) + ",metric=bps;function=derivative;inversion=-1;title=" + nic + "_out")
                        print(now + ",os.nic.bytes." + nic + "_in,"  + str(bytes_recv) + ",metric=bps;function=derivative;inversion=1;title=" + nic + "_in")
 
                        print(now + ",os.nic.packets." + nic + "_sent," + str(packets_sent) + ",metric=pps;function=derivative;inversion=-1;title=" + nic + "_sent")
                        print(now + ",os.nic.packets." + nic + "_recv," + str(packets_recv) + ",metric=pps;function=derivative;inversion=1;title=" + nic + "_recv")

            sys.stdout.flush()
            time.sleep(1)
        except:
            pass
