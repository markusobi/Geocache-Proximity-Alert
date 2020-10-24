#!/usr/bin/env python3
import copy
import pathlib
import re
import sys
import xml.etree.ElementTree as ElementTree
import io

# symbol custom 0 refers to a 24x24 pixel image "H:\Garmin\CustomSymbols\custom 0.bmp"
# color format must be 24 or 8 bit RBG bmp
# color magenta (R, G, B) == (255, 0, 255) is used for transparent pixels
gpx_template = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" creator="eTrex Touch 35t" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackStatsExtension/v1 http://www8.garmin.com/xmlschemas/TrackStatsExtension.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
<metadata>
    <link href="http://www.garmin.com">
        <text>Garmin International</text>
    </link>
    <time>2020-07-20T14:35:10Z</time>
</metadata>
<wpt lat="0.0" lon="0.0">
    <time>2020-07-20T16:29:35Z</time>
    <name>GC00000</name>
    <sym>custom 0</sym>
    <extensions>
        <wptx1:WaypointExtension>
            <wptx1:Proximity>50.0</wptx1:Proximity>
            <wptx1:DisplayMode>SymbolOnly</wptx1:DisplayMode>
        </wptx1:WaypointExtension>
    </extensions>
</wpt>
</gpx>"""


class Geocache(object):
    def __init__(self, name, gc_code, lat, lon, types, difficulty, terrain, hint=None):
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
        # replace xhtml linebreaks
        hint = re.sub("<br\s*?/>", "\n", hint).strip()
        hint = None if hint == "" else hint
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
    print(f"found {len(geocaches)} geocache(s) in {gpx_filepath}")
    return geocaches


def get_xml_namespaces(filename):
    return [(prefix, schema_url) for event, (prefix, schema_url) in ElementTree.iterparse(filename, events=['start-ns'])]


def proximity_alert_tree(geocaches):
    gpx_template_root = ElementTree.fromstring(gpx_template)
    root = gpx_template_root
    template_wpt = root.find("{*}wpt")
    root.remove(template_wpt)
    for geocache in geocaches:
        new_wpt_element = copy.deepcopy(template_wpt)
        new_wpt_element.set("lat", geocache.lat)
        new_wpt_element.set("lon", geocache.lon)
        if geocache.hint is None:
            display_name = "{name} (D{difficulty}/T{terrain})".format(**vars(geocache))
        else:
            display_name = "{name} (D{difficulty}/T{terrain} {hint})".format(**vars(geocache))
        new_wpt_element.find("{*}name").text = display_name
        root.append(new_wpt_element)
    return ElementTree.ElementTree(root)


def main():
    if sys.version_info < (3, 8):
        sys.exit("error: python version too old. python 3.8 or higher is required to run this program")
    gpx_filepaths = sys.argv[1:]
    if len(gpx_filepaths) == 0:
        gpx_filepaths = list(pathlib.Path.cwd().rglob("*.gpx"))
        if len(gpx_filepaths) == 0:
            sys.exit("error: no gpx files given and no gpx files found in current directory")
    geocaches = []
    for gpx_filepath in gpx_filepaths:
        geocaches.extend(read_geocaches(gpx_filepath))
    print(f"{len(geocaches)} geocache(s) found")
    tree = proximity_alert_tree(geocaches)
    # need to register old namespace prefix alias in order to keep it
    for prefix, schema_url in get_xml_namespaces(io.StringIO(gpx_template)):
        ElementTree.register_namespace(prefix, schema_url)
    tree.write("proximity_alarm.gpx")


if __name__ == "__main__":
    main()
    input("Press Enter to continue...")
