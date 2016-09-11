#!/usr/bin/env __PYTHONVER__

import time
import psutil
import sys

if __name__ == "__main__":
    while True:
        try:
            # Get the current unix epoch time
            now = str(int(time.time() / 1))
    
            # Output needs to be in comma format, eg:
            # epoch,checkname,value;metadata
            # Eg:
            # 1425057446,memtotal,8080160,metric=bytes;title=memtotal
            # 1425057446,memfree,263092,metric=bytes;title=memfree
            # 1425057446,memavailable,513388,metric=bytes;title=memavailable

            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            dict_mem = {}
            for name in mem._fields:
                dict_mem.update({str(name): str(getattr(mem, name))})
            dict_swap = {}
            for name in swap._fields:
                dict_swap.update({str(name): str(getattr(swap, name))})

            print(now + ',os.mem.memtotal,' +str(dict_mem['total']) + ",metric=bytes;title=memtotal")
            print(now + ',os.mem.memavail,' +str(dict_mem['available']) + ",metric=bytes;title=memavail")
            print(now + ',os.mem.swapused,' +str(dict_swap['used']) + ",metric=bytes;title=swapused")

            sys.stdout.flush()
            time.sleep(1)

#            mem = psutil.virtual_memory()
#            swap = psutil.swap_memory()

#            print(now + ',os.mem.memtotal,' +str(mem.__dict__['total']) + ",metric=bytes;title=memtotal")
#            print(now + ',os.mem.memavail,' +str(mem.__dict__['available']) + ",metric=bytes;title=memavail")
#            print(now + ',os.mem.swapused,' +str(swap.__dict__['used']) + ",metric=bytes;title=swapused")
 
#            sys.stdout.flush()
#            time.sleep(1)
        except:
            pass

