#!/usr/bin/env python3
import copy
import glob
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


def read_waypoints(gpx_filename):
    waypoints = []
    tree = ElementTree.parse(gpx_filename)
    root = tree.getroot()
    if not root.tag.endswith("}gpx"):
        return []
    for wpt in root.findall("{*}wpt"):
        wpt_type = wpt.find("{*}type")
        if wpt_type is None:
            continue
        types = list(map(str.lower, wpt_type.text.split("|")))
        if "geocache" not in types:
            continue
        waypoints.append(wpt)
    print(f"found {len(waypoints)} geocache(s) in {gpx_filename}")
    return waypoints


def get_xml_namespaces(filename):
    return [(prefix, schema_url) for event, (prefix, schema_url) in ElementTree.iterparse(filename, events=['start-ns'])]


def write_waypoints(waypoints):
    gpx_template_root = ElementTree.fromstring(gpx_template)
    root = gpx_template_root
    template_wpt = root.find("{*}wpt")
    root.remove(template_wpt)
    for waypoint in waypoints:
        new_wpt_element = copy.deepcopy(template_wpt)
        new_wpt_element.set("lat", waypoint.get("lat"))
        new_wpt_element.set("lon", waypoint.get("lon"))
        GC_code = waypoint.find("{*}name").text
        cache_name = waypoint.find(".//{*}cache/{*}name").text
        new_wpt_element.find("{*}name").text = f"{cache_name} ({GC_code})"
        root.append(new_wpt_element)
    return ElementTree.ElementTree(root)


def main():
    gpx_filenames = sys.argv[1:]
    if len(gpx_filenames) == 0:
        gpx_filenames = glob.glob("*.gpx")
        if len(gpx_filenames) == 0:
            sys.exit("error: no gpx files given and no gpx files found in current directory")
    waypoints = []
    for gpx_filename in gpx_filenames:
        waypoints.extend(read_waypoints(gpx_filename))
    print(f"found total {len(waypoints)} geocache(s)")
    tree = write_waypoints(waypoints)
    # need to register old namespace prefix alias in order to keep it
    for prefix, schema_url in get_xml_namespaces(io.StringIO(gpx_template)):
        ElementTree.register_namespace(prefix, schema_url)
    tree.write("proximity_alarm.gpx")


if __name__ == "__main__":
    main()
    input("Press Enter to continue...")
