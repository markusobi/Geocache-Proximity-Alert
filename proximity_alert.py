#!/usr/bin/env python3
import argparse
import copy
import glob
import os
import sys
import typing
import xml.etree.ElementTree as ElementTree
import io
import dataclasses
from typing import Sequence

assert sys.version_info >= (3, 8), "python 3.8 or newer is required to run this program"

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

cache_types = {'Earthcache',
               'Letterbox Hybrid',
               'Multi-cache',
               'Traditional Cache',
               'Unknown Cache',
               'Virtual Cache',
               'Wherigo Cache', }


class ProximityAlertError(Exception):
    pass


@dataclasses.dataclass
class Geocache:
    name: str
    gc_code: str
    lat: str
    lon: str
    cache_type: str
    difficulty: str
    terrain: str
    hint: str


def get_filename(file_or_filename):
    if isinstance(file_or_filename, io.TextIOWrapper):
        return file_or_filename.name
    else:
        return str(file_or_filename)


def get_xml_attribute_value(element: ElementTree.Element, attribute: str) -> str:
    attr_value = element.get(attribute)
    if attr_value is None:
        raise ProximityAlertError(f"failed to find attribute {attribute} in xml element {element.tag}")
    return attr_value


def get_xml_child(parent: ElementTree.Element, child_name: str) -> ElementTree.Element:
    child = parent.find(child_name)
    if child is None:
        raise ProximityAlertError(f"failed to find xml element {child_name} in xml element {parent.tag}")
    return child


def get_xml_text(element: ElementTree.Element) -> str:
    if element.text is None:
        raise ProximityAlertError(f"xml element {element.tag} is empty")
    return element.text


def get_xml_child_text(parent: ElementTree.Element, child_name: str) -> str:
    return get_xml_text(get_xml_child(parent, child_name))


def read_geocaches(gpx_filepath) -> Sequence[Geocache]:
    geocaches = []
    try:
        tree = ElementTree.parse(gpx_filepath)
    except ElementTree.ParseError as e:
        raise ProximityAlertError("{} is not a valid xml file: {}".format(get_filename(gpx_filepath), e))
    root_element = tree.getroot()
    if not root_element.tag.endswith("}gpx"):
        raise ProximityAlertError("{} is not a valid gpx file".format(get_filename(gpx_filepath)))
    for wpt_element in root_element.findall("{*}wpt[{*}name][{*}type][@lat][@lon]"):
        cache_element = wpt_element.find(".//{*}cache[{*}name][{*}difficulty][{*}terrain][{*}encoded_hints]")
        if cache_element is None:
            continue
        lat = get_xml_attribute_value(wpt_element, "lat")
        lon = get_xml_attribute_value(wpt_element, "lon")
        gc_code = get_xml_child_text(wpt_element, "{*}name")

        name = get_xml_child_text(cache_element, "{*}name")
        cache_type = get_xml_child_text(cache_element, "{*}type")
        difficulty = get_xml_child_text(cache_element, "{*}difficulty")
        terrain = get_xml_child_text(cache_element, "{*}terrain")
        hint_element = get_xml_child(cache_element, "{*}encoded_hints")
        hint = hint_element.text if hint_element.text is not None else ""
        geocache = Geocache(name=name,
                            gc_code=gc_code,
                            lat=lat,
                            lon=lon,
                            cache_type=cache_type,
                            difficulty=difficulty,
                            terrain=terrain,
                            hint=hint)
        geocaches.append(geocache)
    return geocaches


@dataclasses.dataclass
class XMLNamespace:
    prefix: str
    schema_url: str


def get_xml_namespaces(input_file: typing.IO) -> Sequence[XMLNamespace]:
    return [XMLNamespace(prefix=ns_prefix, schema_url=schema_url)
            for event, (ns_prefix, schema_url) in ElementTree.iterparse(input_file, events=['start-ns'])]


def proximity_alert_tree(geocaches: Sequence[Geocache], distance: float) -> ElementTree.ElementTree:
    gpx_template_root = ElementTree.fromstring(gpx_template)
    root = gpx_template_root
    template_wpt = root.find("{*}wpt")
    if template_wpt is None:
        raise ProximityAlertError("internal error: failed to find wpt xml element in gpx template")
    root.remove(template_wpt)
    garmin_waypoint_display_max_text_length = 30
    for geocache in geocaches:
        if len(geocache.name) <= garmin_waypoint_display_max_text_length:
            display_text = geocache.name
        else:
            display_text = geocache.name[:6] + "~" + geocache.name[-23:]
        proximity_wpt = copy.deepcopy(template_wpt)
        proximity_wpt.set("lat", geocache.lat)
        proximity_wpt.set("lon", geocache.lon)
        wpt_name = proximity_wpt.find("{*}name")
        if wpt_name is None:
            raise ProximityAlertError("internal error: failed to find name xml element in gpx template")
        wpt_name.text = display_text
        wpt_distance = proximity_wpt.find("{*}extensions/{*}WaypointExtension/{*}Proximity")
        if wpt_distance is None:
            raise ProximityAlertError("internal error: failed to find Proximity xml element in gpx template")
        wpt_distance.text = str(distance)
        root.append(proximity_wpt)
    return ElementTree.ElementTree(root)


def create_alert(gpx_filepaths, out_file_or_filename, distance: float, verbose: bool):
    geocaches: typing.List[Geocache] = []
    for gpx_filepath in gpx_filepaths:
        geocaches_found = read_geocaches(gpx_filepath)
        if verbose:
            print(f"{len(geocaches_found):>4} geocache(s) found in {get_filename(gpx_filepath)}")
        geocaches.extend(geocaches_found)
    if len(geocaches) == 0:
        return len(geocaches)
    tree = proximity_alert_tree(geocaches, distance)
    # need to register old namespace prefix alias in order to keep it
    for xml_namespace in get_xml_namespaces(io.StringIO(gpx_template)):
        ElementTree.register_namespace(xml_namespace.prefix, xml_namespace.schema_url)
    try:
        tree.write(out_file_or_filename, encoding="utf-8", xml_declaration=True)
    except OSError as e:
        raise ProximityAlertError("failed to write to file {}: {}".format(out_file_or_filename, e))
    if verbose:
        print(f"{len(geocaches):>4} total proximity alert waypoint(s) written to {get_filename(out_file_or_filename)}")
    return len(geocaches)


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("gpx_input_files", nargs="*", type=argparse.FileType("r", encoding="utf-8"),
                        help="input files containing geocaches in gpx format")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="use all gpx files in the current working directory (recursive search)"
                             " as gpx input files")
    parser.add_argument("-o", "--output", type=str, default="proximity_alert.gpx",
                        help="filename to which this tool will write proximity waypoints to (default: %(default)s)")
    parser.add_argument("--distance", type=float, default=50.0,
                        help="alert radius in meters around a geocache (default: %(default)s)")
    parser.add_argument("--verbose", action="store_true",
                        help="print extra information")
    parser.add_argument('--version', action='version', version='geocache proximity alert 0.2preview')
    options = parser.parse_args(args)

    if options.recursive:
        gpx_input_files = sorted(glob.glob("**/*.gpx", recursive=True))
        # exclude output file if it already exists
        if os.path.isfile(options.output):
            gpx_input_files = [path for path in gpx_input_files
                               if not os.path.samefile(path, options.output)]
        options.gpx_input_files = gpx_input_files
        if len(options.gpx_input_files) == 0:
            raise ProximityAlertError("error: no gpx input files found in current working directory")
    else:
        if len(options.gpx_input_files) == 0:
            raise ProximityAlertError("error: no gpx input files given")
    return options


def main(args: Sequence[str]):
    try:
        options = parse_args(args)

        num_caches_found = create_alert(
            gpx_filepaths=options.gpx_input_files,
            out_file_or_filename=options.output,
            distance=options.distance,
            verbose=options.verbose)

        if num_caches_found == 0:
            raise ProximityAlertError("error: no geocaches found in gpx file(s)")
    except ProximityAlertError as e:
        sys.exit(e)


if __name__ == "__main__":
    main(sys.argv)
