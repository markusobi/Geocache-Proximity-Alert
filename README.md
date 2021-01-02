# Geocache Proximity Alert
Generates proximity alert waypoints for garmin devices from `.gpx` geocache files.

## Requirements
 - Python 3.8 or higher (Windows download: https://www.python.org/downloads/)

## Getting Started
### Installation
 - Copy [proximity_alert.py](proximity_alert.py) and [run.bat](run.bat) to a folder containing geocache .gpx files (i.e. to `Garmin\GPX\geocaches\`).
 - Copy [custom 0.bmp](custom&#32;0.bmp) to `Garmin\CustomSymbols\`. This will make the icons of the proximity waypoints invisible on the garmin device. This step is optional.
### Running
The following will create a `proximity_alert.gpx` file containing proximity alert waypoints for all caches found in all `.gpx` files in the current working directory (recursive search).
 #### Windows
 - Execute [run.bat](run.bat).
#### Linux/macOS
 - Run `python3 proximity_alert.py --recursive --verbose`
## Tested on the following Garmin devices:
 - eTrex Touch 35t
