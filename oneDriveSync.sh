#!/bin/bash

NOW=$(date +"%Y-%m-%d-%H-%M-%S-%N")

if [ -e /mnt/sentinel.txt ]
then
    echo "Sentinel exists, proceed with sync"
    rclone sync -v onedrive: /mnt/onedriveBackup/ --retries 1 --ignore-errors --log-file "/home/pi/syncLogs/oneDriveRclone-Log-$NOW.log"

else
    echo "Could not find sentinel file, will not sync"
fi

