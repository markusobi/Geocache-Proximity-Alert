@echo off
py proximity_alert.py --verbose --recursive --output proximity_alert_5m.gpx --distance 5
py proximity_alert.py --verbose --recursive --output proximity_alert_50m.gpx --distance 50
pause
