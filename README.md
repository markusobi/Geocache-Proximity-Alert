# Geocache Proximity Alert
This is a command line tool that can be used to make a Garmin device raise a proximity alarm when a geocache is closer than a certain distance.
This tool takes one or more geocache `.gpx` files as input and generates a `.gpx` output file.
The generated `.gpx` file contains one gpx-waypoint for each cache.
If this generated `.gpx` is placed inside the `Garmin\GPX\` folder, the Garmin device will raise an alarm every time one of these gpx-waypoints is near.

## Requirements
 - Python 3.8 or higher (Windows download: https://www.python.org/downloads/)

## Getting Started
### Running
The following will create a `proximity_alert.gpx` file containing proximity alert waypoints for all caches found in all `.gpx` files in the current working directory (recursive search). It is not necessary to put this tool onto your Garmin device, but this will save you the manual copying each time you generate the `proximity_alert.gpx` file. You have two options:
#### A: Using proximity_alert.exe (Windows only)
 - Copy your geocache `.gpx` files to your Garmin device into `Garmin\GPX\geocaches\`
 - Download [geocache_proximity_alert-...-windows-x86.zip](https://github.com/markusobi/Geocache-Proximity-Alert/releases) and extract content to `Garmin\GPX\geocaches\`
 - Run `Garmin\GPX\geocaches\proximity_alert.bat` inside `Garmin\GPX\geocaches\`
#### B: Using proximity_alert.py (python script, any OS)
 - Copy your geocache `.gpx` files to your Garmin device into `Garmin\GPX\geocaches\`
 - Install Python 3.8 (or higher)
 - Download [geocache_proximity_alert-...-python.zip](https://github.com/markusobi/Geocache-Proximity-Alert/releases) and extract content to `Garmin\GPX\geocaches\`
 - Run `python3 proximity_alert.py --recursive --verbose` (On Windows use command `python` instead or specify full path to `python.exe` if python is not in your PATH)

### How to hide the additional waypoint symbols (blue flags)
 - Copy [custom 0.bmp](https://raw.githubusercontent.com/markusobi/Geocache-Proximity-Alert/master/custom%200.bmp) to `Garmin\CustomSymbols\`. This will make the icons of the proximity waypoints invisible on the garmin device. See [Saving a Custom Symbol to a Device](https://support.garmin.com/?faq=VTS8XTdjCW5Tx3HyfJ3eQ6).
 - Copy [custom 0.bmp](https://raw.githubusercontent.com/markusobi/Geocache-Proximity-Alert/master/custom%200.bmp) to `C:\Users\%USERNAME%\Documents\My Garmin\Custom Waypoint Symbols\` and rename it to `000.BMP`. This will make the proximity waypoints invisible in BaseCamp. See [Creating a Custom Symbol](https://support.garmin.com/?faq=VTS8XTdjCW5Tx3HyfJ3eQ6).

## Command-Line Reference
```
usage: proximity_alert.py [-h] [-r] [-o OUTPUT] [--distance DISTANCE] [--verbose] [--version] [gpx_input_files [gpx_input_files ...]]

positional arguments:
  gpx_input_files       input files containing geocaches in gpx format

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       use all gpx files in the current working directory (recursive search) as gpx input files
  -o OUTPUT, --output OUTPUT
                        filename to which this tool will write proximity waypoints to (default: proximity_alert.gpx)
  --distance DISTANCE   alert radius in meters around a geocache (default: 50.0)
  --verbose             print extra information
  --version             show program's version number and exit
```

## Tested on the following Garmin devices:
 - eTrex Touch 35t
