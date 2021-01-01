#!/usr/bin/env python3
import glob
import re
import xml.etree.ElementTree as ElementTree


def get_xml_namespaces(xml_file_or_filename):
    return [(prefix, schema_url) for event, (prefix, schema_url) in
            ElementTree.iterparse(xml_file_or_filename, events=['start-ns'])]


def fix_namespaces(xml_file_or_filename):
    # need to register old namespace prefix alias in order to keep it
    for prefix, schema_url in get_xml_namespaces(xml_file_or_filename):
        ElementTree.register_namespace(prefix, schema_url)


def main():
    for testcase_dir in glob.glob("*/"):
        for gpx_path in glob.glob(testcase_dir + "in/*.gpx"):
            tree = ElementTree.parse(gpx_path)
            root = tree.getroot()
            for node in root.iterfind(".//{*}logs/"):
                node.clear()
            for node in root.iterfind(".//{*}long_description"):
                node.clear()
            fix_namespaces(gpx_path)
            tree.write(gpx_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
