#!/bin/bash
find /home/pi/syncLogs/ -name "oneDriveRclone*.log" -type f -mtime +30 -delete
