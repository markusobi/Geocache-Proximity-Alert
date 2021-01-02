# Geocache Proximity Alert
Generates proximity alert waypoints for garmin devices from `.gpx` geocache files.

## Requirements
 - Python 3.8 or higher (Windows download: https://www.python.org/downloads/)

## Getting Started
 - Copy [proximity_alert.py](proximity_alert.py) and [run.bat](run.bat) to a folder containing geocache .gpx files (i.e. to `Garmin\GPX\geocaches\`).
 - Copy [custom 0.bmp](custom&#32;0.bmp) to `Garmin\CustomSymbols\`. This will make the icons of the proximity waypoints invisible on the garmin device. This step is optional.
 - Execute [run.bat](run.bat). This will create a `proximity_alert.gpx` file containing proximity alert waypoints for all caches found in all `.gpx` files in the current working directory (recursive search).
## Tested Garmin Devices:
 - eTrex Touch 35t
