#!/usr/bin/env __PYTHONVER__

import psutil
import time
import sys
import subprocess


if __name__ == "__main__":
    # Output needs to be in comma format, eg:
    # epoch,checkname,value,metadata
    # Eg:
    # 1430157858,os.disk.bytes.sda1_write,32863319809,metric=bps;title=sda1_write
    # 1430157858,os.disk.bytes.sda1_read,6320095757,metric=bps;title=sda1_read 
    # 1430157858,os.disk.bytes.sdb1_write,4128073428,metric=bps;title=sdb1_write
    # 1430157858,os.disk.bytes.sdb1_read,3156351939,metric=bps;title=sdb1_read

    # List of disk IO devices we want to track in key:value pairs
    # Matched on the base name of the device. Eg: sdc4 will match because we track "sd"
    # The value part of the key is the renamed part of the device. Eg, we can rename sr to 'sd'
    filterdisks = ['sr', 'cdrom', 'ram']

    while True:
        # Get the current unix epoch time
        now = str(int(time.time() / 1))
        disks = psutil.disk_io_counters(perdisk=True)

        for disk in disks:
            if len(disks[disk]) == 6:
                (read_count, write_count, read_bytes, write_bytes, read_time, write_time) = disks[disk]
            if len(disks[disk]) == 9:
                (read_count, write_count, read_bytes, write_bytes, read_time, write_time, read_merged_count, write_merged_count, busy_time) = disks[disk]


            if (disk[:-2] not in filterdisks) and (disk[:-1] not in filterdisks):
                disktitle = diskname = disk

                # For dm- devices, we need to find out where it links to and use that as the proper name
                # Call the command: lsblk -n -o NAME /dev/dm-1
                if 'dm-' in diskname:
                    try:
                        disktitle = subprocess.check_output(["lsblk", "-n", "-o", "name", "/dev/" + diskname.strip()]).split()[0]
                    except:
                        pass                        

                print(now + ",os.disk.bytesio." + diskname + "_write," + str(write_bytes) + ",metric=bps;axisleftright=right;axisylabel=Writes in bps;function=derivative;title=" + disktitle.strip() + "_write")
                print(now + ",os.disk.bytesio." + diskname + "_read,"  + str(read_bytes)  + ",metric=bps;axisleftright=left;axisylabel=Reads in bps;function=derivative;title=" + disktitle.strip() + "_read")

        sys.stdout.flush()
        time.sleep(1)


