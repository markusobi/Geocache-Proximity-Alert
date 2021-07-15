# Geocache Proximity Alert
## What it does
This is a command line tool that can be used to make a Garmin device raise an acoustic alert every time the distance to a geocache falls below a certain threshold.
## How it works
This command line tool takes one or more geocache `.gpx` files as input and generates a `.gpx` output file (default: `proximity_alert.gpx`).
The generated `.gpx` file contains one additional proximity gpx-waypoint for each cache.
If this generated `.gpx` is placed inside the `Garmin\GPX\` folder, the Garmin device will raise an alert every time a geocache is near.

## How to Install
The following instructions assume that your geocache GPX files are stored in `Garmin\GPX\geocaches\` on your Garmin device.
 - Install Python 3.8 or higher (Windows download: https://www.python.org/downloads/) and ensure that the location of python.exe is in your PATH variable.
 - Download the latest release [geocache_proximity_alert-...-python.zip](https://github.com/markusobi/Geocache-Proximity-Alert/releases) and extract content to `Garmin\GPX\geocaches\`.
## How to Run
The following will create a `proximity_alert.gpx` file containing proximity alert waypoints for all caches found in all `.gpx` files in the current working directory (recursive search).
 - Open `cmd` in `Garmin\GPX\geocaches\`.
 - Run command `python.exe proximity_alert.py --recursive --verbose`.

## How to hide the proximity alarm waypoint symbols on the Garmin device
 - Download [custom 0.bmp](https://raw.githubusercontent.com/markusobi/Geocache-Proximity-Alert/master/custom%200.bmp) and save it to `Garmin\CustomSymbols\`.

This will make the icons of the proximity waypoints invisible on the Garmin device. Reference: [Saving a Custom Symbol to a Device](https://support.garmin.com/?faq=VTS8XTdjCW5Tx3HyfJ3eQ6).
## How to hide the proximity alarm waypoint symbols in Basecamp
 - Navigate to `C:\Users\%USERNAME%\Documents\My Garmin\Custom Waypoint Symbols\`.
 - Delete or rename any existing `000.BMP` or `000.png` files.
 - Download [custom 0.bmp](https://raw.githubusercontent.com/markusobi/Geocache-Proximity-Alert/master/custom%200.bmp) and save it as `000.BMP`. Reference: [Creating a Custom Symbol](https://support.garmin.com/?faq=VTS8XTdjCW5Tx3HyfJ3eQ6).

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
