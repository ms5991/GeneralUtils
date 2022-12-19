#!/bin/bash
find /home/pi/pingMonitor/pingMonitorLogs/ -name "*.log" -type f -mtime +10 -delete
