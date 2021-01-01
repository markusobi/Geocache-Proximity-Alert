# Geocache Proximity Alert
Generates proximity alert waypoints for garmin devices from `.gpx` geocache files.

## Requirements
 - Python 3.8 or higher

## Getting Started
 - Copy [proximity_alert.py](proximity_alert.py) to a folder containing geocache .gpx files (i.e. to `Garmin\GPX\geocaches\`).
 - Execute [proximity_alert.py](proximity_alert.py). This will create a `proximity_alert.gpx` file containing proximity alert waypoints for all caches found in all `.gpx` files in the current working directory (recursive search).
 - Copy [custom 0.bmp](custom&#32;0.bmp) to `Garmin\CustomSymbols\`. This will make the icons of the proximity waypoints invisible on the garmin device.
## Tested Garmin Devices:
 - eTrex Touch 35t
