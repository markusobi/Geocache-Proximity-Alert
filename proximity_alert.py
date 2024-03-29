#!/usr/bin/env python3
import argparse
import copy
import glob
import os
import sys
import xml.etree.ElementTree as ElementTree
import io
import dataclasses
import pathlib
from typing import Sequence, List, Union, IO, AnyStr

assert sys.version_info >= (3, 8), "python 3.8 or newer is required to run this program"

# symbol custom 0 refers to a 24x24 pixel image "H:\Garmin\CustomSymbols\custom 0.bmp"
# color format must be 24 bit or 8 bit RBG bmp
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


def get_xml_attribute_value(element: ElementTree.Element, attribute: str) -> str:
    attr_value = element.get(attribute)
    if attr_value is None:
        raise ProximityAlertError(f"error: failed to find attribute {attribute} in xml element {element.tag}")
    return attr_value


def find_xml_child(parent: ElementTree.Element, child_name: str) -> ElementTree.Element:
    child = parent.find(child_name)
    if child is None:
        raise ProximityAlertError(f"error: failed to find xml element {child_name} in xml element {parent.tag}")
    return child


def get_xml_text(element: ElementTree.Element) -> str:
    if element.text is None:
        raise ProximityAlertError(f"error: xml element {element.tag} is empty")
    return element.text


def find_xml_child_and_get_text(parent: ElementTree.Element, child_name: str) -> str:
    return get_xml_text(find_xml_child(parent, child_name))


def read_geocaches(gpx_filepath: Union[str, pathlib.Path]) -> Sequence[Geocache]:
    geocaches = []
    try:
        tree = ElementTree.parse(gpx_filepath)
    except Exception as e:
        raise ProximityAlertError(f"error: failed to open/parse xml file {gpx_filepath}: {e}")
    root_element = tree.getroot()
    if not root_element.tag.endswith("}gpx"):
        raise ProximityAlertError(f"error: failed to find gpx element in file {gpx_filepath}")
    for wpt_element in root_element.findall("{*}wpt[{*}name][{*}type][@lat][@lon]"):
        cache_element = wpt_element.find(".//{*}cache[{*}name][{*}difficulty][{*}terrain][{*}encoded_hints]")
        if cache_element is None:
            continue

        hint_element = find_xml_child(cache_element, "{*}encoded_hints")
        hint = hint_element.text if hint_element.text is not None else ""

        geocache = Geocache(name=find_xml_child_and_get_text(cache_element, "{*}name"),
                            gc_code=find_xml_child_and_get_text(wpt_element, "{*}name"),
                            lat=get_xml_attribute_value(wpt_element, "lat"),
                            lon=get_xml_attribute_value(wpt_element, "lon"),
                            cache_type=find_xml_child_and_get_text(cache_element, "{*}type"),
                            difficulty=find_xml_child_and_get_text(cache_element, "{*}difficulty"),
                            terrain=find_xml_child_and_get_text(cache_element, "{*}terrain"),
                            hint=hint)
        geocaches.append(geocache)
    return geocaches


def register_namespace_prefixes_globally(input_file: IO[AnyStr]) -> None:
    for event, (ns_prefix, schema_url) in ElementTree.iterparse(input_file, events=['start-ns']):
        ElementTree.register_namespace(ns_prefix, schema_url)


def proximity_alert_tree(geocaches: Sequence[Geocache], distance: float) -> ElementTree.ElementTree:
    gpx_template_root = ElementTree.fromstring(gpx_template)
    root = gpx_template_root
    template_wpt = find_xml_child(root, "{*}wpt")
    root.remove(template_wpt)
    garmin_max_display_text_length = 30
    for geocache in geocaches:
        if len(geocache.name) <= garmin_max_display_text_length:
            display_text = geocache.name
        else:
            display_text = geocache.name[:10] + "~" + geocache.name[-19:]
        proximity_wpt = copy.deepcopy(template_wpt)
        proximity_wpt.set("lat", geocache.lat)
        proximity_wpt.set("lon", geocache.lon)
        wpt_name = find_xml_child(proximity_wpt, "{*}name")
        # BaseCamp cannot display multiple waypoints with the same name.
        # That's why the distance is added to the name.
        # This way multiple proximity circles can be seen in BaseCamp.
        wpt_name.text = f"{display_text} {round(distance)}m"
        wpt_distance = find_xml_child(proximity_wpt, "{*}extensions/{*}WaypointExtension/{*}Proximity")
        wpt_distance.text = str(distance)
        root.append(proximity_wpt)
    return ElementTree.ElementTree(root)


def create_alert(
        gpx_filepaths: Sequence[str],
        out_file_or_path: Union[str, IO[AnyStr]],
        distance: float,
        verbose: bool) -> int:
    geocaches: List[Geocache] = []
    for gpx_filepath in gpx_filepaths:
        geocaches_found = read_geocaches(gpx_filepath)
        if verbose:
            print(f"{len(geocaches_found):>4} geocache(s) found in {gpx_filepath}")
        geocaches.extend(geocaches_found)
    if len(geocaches) == 0:
        return len(geocaches)
    xml_tree = proximity_alert_tree(geocaches, distance)
    # need to register old xml namespace prefixes to keep it
    register_namespace_prefixes_globally(io.StringIO(gpx_template))
    try:
        xml_tree.write(out_file_or_path, encoding="utf-8", xml_declaration=True)
    except OSError as e:
        raise ProximityAlertError(f"error: failed to write to file {out_file_or_path}: {e}")
    if verbose:
        print(f"{len(geocaches):>4} total proximity alert waypoint(s) written to {out_file_or_path}")
    return len(geocaches)


@dataclasses.dataclass
class Options:
    gpx_input_files: List[str]
    output: str
    distance: float
    verbose: bool


def parse_args(args: Sequence[str]) -> Options:
    parser = argparse.ArgumentParser()
    parser.add_argument("gpx_input_files", nargs="*", type=str,
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
        if len(options.gpx_input_files) != 0:
            raise ProximityAlertError("error: input files may not be provided when using --recursive")
        gpx_input_files = sorted(glob.glob("**/*.gpx", recursive=True))

        def is_not_output_file(path: str) -> bool:
            try:
                return not os.path.samefile(path, options.output)
            except FileNotFoundError:
                return True

        # filter out output file
        gpx_input_files = list(filter(is_not_output_file, gpx_input_files))
        if len(gpx_input_files) == 0:
            raise ProximityAlertError("error: no gpx input files found in current working directory")
    else:
        if len(options.gpx_input_files) == 0:
            raise ProximityAlertError("error: no gpx input files given and --recursive is not set")
        gpx_input_files = options.gpx_input_files
    return Options(gpx_input_files=gpx_input_files,
                   output=options.output,
                   distance=options.distance,
                   verbose=options.verbose)


def main(args: Sequence[str]) -> None:
    try:
        options = parse_args(args)

        num_caches_found = create_alert(
            gpx_filepaths=options.gpx_input_files,
            out_file_or_path=options.output,
            distance=options.distance,
            verbose=options.verbose)

        if num_caches_found == 0:
            raise ProximityAlertError("error: no geocaches found in gpx file(s)")
    except ProximityAlertError as e:
        sys.exit(e)


if __name__ == "__main__":
    main(sys.argv[1:])
