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
            # 1425057446,os.cpu.usage.user,0.56,metric=percent;title=user
            # 1425057446,os.cpu.usage.idle,0.23,metric=percent;title=idle
            # 1425057446,os.cpu.usage.system,0.11,metric=percent;title=system
    
            cpusage = psutil.cpu_times_percent(interval=1, percpu=False)

            dict_cpu = {}
            for name in cpusage._fields:
                dict_cpu.update({str(name): getattr(cpusage, name)})

            print(now + ",os.cpu.usage.user," + str(round(dict_cpu['user'])) + ",metric=percent;title=user")
            print(now + ",os.cpu.usage.idle," + str(round(dict_cpu['idle'])) + ",metric=percent;title=idle")
            print(now + ",os.cpu.usage.iowait," + str(round(dict_cpu['iowait'])) + ",metric=percent;title=iowait")

            the_rest = dict_cpu['nice'] + dict_cpu['system'] + dict_cpu['irq'] + dict_cpu['softirq'] + dict_cpu['steal'] + dict_cpu['guest']
            if dict_cpu['guest_nice']: # Doesn't always exist
                the_rest += dict_cpu['guest_nice']

            print(now + ",os.cpu.usage.system," + str(round(the_rest)) + ",metric=percent;title=system")

            sys.stdout.flush()
        except:
            pass

