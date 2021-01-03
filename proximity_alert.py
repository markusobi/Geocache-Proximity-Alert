#!/usr/bin/env python3
import copy
import glob
import os
import re
import sys
import xml.etree.ElementTree as ElementTree
import io

# symbol custom 0 refers to a 24x24 pixel image "H:\Garmin\CustomSymbols\custom 0.bmp"
# color format must be 24 or 8 bit RBG bmp
# color magenta (R, G, B) == (255, 0, 255) is used for transparent pixels
gpx_template = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1"
    xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
    xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1"
    creator="Geocache Proximity Alert"
    version="1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
        http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd
        http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd
        http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd">
<metadata>
    <link href="https://github.com/markusobi/Geocache-Proximity-Alert">
        <text>Created by Geocache Proximity Alert</text>
    </link>
</metadata>
<wpt lat="0.0" lon="0.0">
    <name>GC00000</name>
    <sym>custom 0</sym>
    <extensions>
        <wptx1:WaypointExtension>
            <wptx1:Proximity>0.0</wptx1:Proximity>
            <wptx1:DisplayMode>SymbolOnly</wptx1:DisplayMode>
        </wptx1:WaypointExtension>
    </extensions>
</wpt>
</gpx>"""


class Geocache(object):
    def __init__(self, name, gc_code, lat, lon, types, difficulty, terrain, hint):
        self.name = name
        self.gc_code = gc_code
        self.lat = lat
        self.lon = lon
        self.types = types
        self.difficulty = difficulty
        self.terrain = terrain
        self.hint = hint


def read_geocaches(gpx_filepath):
    geocaches = []
    tree = ElementTree.parse(gpx_filepath)
    root = tree.getroot()
    if not root.tag.endswith("}gpx"):
        return []
    for wpt in root.findall("{*}wpt[{*}type][{*}name][@lat][@lon]"):
        wpt_type = wpt.find("{*}type")
        types = wpt_type.text.split("|")
        # pocket queries have an extra type field
        types2 = wpt.find("{*}extensions/{*}cache/{*}type")
        if types2 is not None:
            types.extend(types2.text.split("|"))
        if "geocache" not in map(str.lower, types):
            continue
        name_element = wpt.find(".//{*}cache/{*}name")
        if name_element is None:
            continue
        gc_code = wpt.find("{*}name").text
        difficulty = wpt.find(".//{*}cache/{*}difficulty").text
        terrain = wpt.find(".//{*}cache/{*}terrain").text
        hint = wpt.find(".//{*}cache/{*}encoded_hints").text
        if hint is None:
            hint = ""
        else:
            # replace xhtml linebreaks in hints
            hint = re.sub(r"<br\s*?/>", "\n", hint).strip()
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        geocache = Geocache(name=name_element.text,
                            gc_code=gc_code,
                            lat=lat,
                            lon=lon,
                            types=types,
                            difficulty=difficulty,
                            terrain=terrain,
                            hint=hint)
        geocaches.append(geocache)
    return geocaches


def get_xml_namespaces(filename):
    return [(prefix, schema_url) for event, (prefix, schema_url) in
            ElementTree.iterparse(filename, events=['start-ns'])]


def proximity_alert_tree(geocaches, distance, display_format):
    gpx_template_root = ElementTree.fromstring(gpx_template)
    root = gpx_template_root
    template_wpt = root.find("{*}wpt")
    root.remove(template_wpt)
    for geocache in geocaches:
        new_wpt_element = copy.deepcopy(template_wpt)
        new_wpt_element.set("lat", geocache.lat)
        new_wpt_element.set("lon", geocache.lon)
        new_wpt_element.find("{*}name").text = display_format.format(**vars(geocache))
        new_wpt_element.find("{*}extensions/{*}WaypointExtension/{*}Proximity").text = str(distance)
        root.append(new_wpt_element)
    return ElementTree.ElementTree(root)


def get_filename(file_or_filename):
    if isinstance(file_or_filename, io.TextIOWrapper):
        return file_or_filename.name
    else:
        return str(file_or_filename)


def create_alert(gpx_filepaths, out_file_or_filename, distance, display_format, verbose):
    geocaches = []
    for gpx_filepath in gpx_filepaths:
        geocaches_found = read_geocaches(gpx_filepath)
        if verbose:
            print(f"{len(geocaches_found):>4} geocache(s) found in {get_filename(gpx_filepath)}")
        geocaches.extend(geocaches_found)

    tree = proximity_alert_tree(geocaches, distance, display_format)
    # need to register old namespace prefix alias in order to keep it
    for prefix, schema_url in get_xml_namespaces(io.StringIO(gpx_template)):
        ElementTree.register_namespace(prefix, schema_url)
    tree.write(out_file_or_filename, encoding="utf-8", xml_declaration=True)
    if verbose:
        print(f"{len(geocaches):>4} total proximity alert waypoint(s) written to {get_filename(out_file_or_filename)}")


def parse_args(args):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("gpx_input_files", nargs="*", type=argparse.FileType("r", encoding="utf-8"),
                        help="input files containing geocaches in gpx format")
    parser.add_argument("-r", "--recursive", action=argparse.BooleanOptionalAction, default=False,
                        help="use all gpx files in the current working directory (recursive search)"
                             " as gpx input files")
    parser.add_argument("-o", "--output", type=str, default="proximity_alert.gpx",
                        help="output filename"
                             "this tool will write proximity waypoints in gpx format to it (default: %(default)s)")
    parser.add_argument("--distance", type=float, default=50.0,
                        help="alert radius in meters around a geocache (default: %(default)s)")
    parser.add_argument("--displayformat", type=str,
                        default="{gc_code}\n"
                                "D{difficulty}/T{terrain}\n"
                                "{hint}\n"
                                "{name}",
                        help="custom display format string (default: %(default)s). "
                             "supported vars: [name, gc_code, lat, lon, difficulty, terrain, hint]")
    parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction, default=False,
                        help="print extra information")
    options = parser.parse_args(args)

    if options.recursive:
        gpx_input_files = [path for path in glob.glob("**/*.gpx", recursive=True)]
        # exclude output file if it already exists
        if os.path.isfile(options.output):
            gpx_input_files = [path for path in gpx_input_files
                               if not os.path.samefile(path, options.output)]
        options.gpx_input_files = gpx_input_files
        if len(options.gpx_input_files) == 0:
            sys.exit("error: no gpx input files found in current working directory")
    else:
        if len(options.gpx_input_files) == 0:
            sys.exit("error: no gpx input files given")
    return options


def main():
    options = parse_args(sys.argv[1:])

    create_alert(gpx_filepaths=options.gpx_input_files,
                 out_file_or_filename=options.output,
                 distance=options.distance,
                 display_format=options.displayformat,
                 verbose=options.verbose)


if __name__ == "__main__":
    main()
