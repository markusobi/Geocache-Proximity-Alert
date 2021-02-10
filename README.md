# Geocache Proximity Alert
Generates proximity alert waypoints for garmin devices from `.gpx` geocache files.

## Requirements
 - Python 3.8 or higher (Windows download: https://www.python.org/downloads/)

## Getting Started
### Installation
 - Copy [proximity_alert.py](proximity_alert.py) and [run.bat](run.bat) to a folder containing geocache .gpx files (i.e. to `Garmin\GPX\geocaches\`).
 - Copy [custom 0.bmp](custom&#32;0.bmp) to `Garmin\CustomSymbols\`. This will make the icons of the proximity waypoints invisible on the garmin device. See [Saving a Custom Symbol to a Device](https://support.garmin.com/?faq=VTS8XTdjCW5Tx3HyfJ3eQ6).
 - Copy [custom 0.bmp](custom&#32;0.bmp) to `C:\Users\%USERNAME%\Documents\My Garmin\Custom Waypoint Symbols\` and rename it to `000.BMP`. This will make the proximity waypoints invisible in basecamp. See [Creating a Custom Symbol](https://support.garmin.com/?faq=VTS8XTdjCW5Tx3HyfJ3eQ6).

### Running
The following will create a `proximity_alert.gpx` file containing proximity alert waypoints for all caches found in all `.gpx` files in the current working directory (recursive search).
 #### Windows
 - Execute [run.bat](run.bat).
#### Linux/macOS
 - Run `python3 proximity_alert.py --recursive --verbose`
## Tested on the following Garmin devices:
 - eTrex Touch 35t
