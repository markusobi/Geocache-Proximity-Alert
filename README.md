# Geocache Proximity Alert
Generates proximity alarm waypoints for garmin devices from `.gpx` geocache files.

## Requirements
 - Python 3.8 or higher

## Getting Started
 - Copy [proximity_alarm.py](proximity_alarm.py) to a folder containing geocache .gpx files (i.e. to `Garmin\GPX\geocaches\`).
 - Execute [proximity_alarm.py](proximity_alarm.py). This will create a `proximity_alarm.gpx` file containing proximity alarm waypoints for all caches found in all `.gpx` files in the current working directory (recursive search).
 - Copy [custom 0.bmp](custom&#32;0.bmp) to `Garmin\CustomSymbols\`. This will make the icons of the proximity waypoints invisible on the garmin device.
## Tested Garmin Devices:
 - eTrex Touch 35t
