# Geocache Proximity Alert
Generates proximity alarm waypoints for garmin devices from .gpx geocache files.

## Requirements
 - Python3.8 or higher

## Getting Started
 - copy proximity_alarm.py to folder containing .gpx files (i.e. `Garmin\GPX\`)
 - executing [proximity_alarm.py](proximity_alarm.py) will create a `proximity_alarm.gpx` file containing proximity alarm waypoints for all caches found in all .gpx files of the current working directory
 - copy [custom 0.bmp](custom 0.bmp) to `Garmin\CustomSymbols\`