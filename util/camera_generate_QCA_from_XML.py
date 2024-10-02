import argparse
import os
import xml.etree.ElementTree as ET

import numpy as np

# Parse the XML file


def parseXML(in_path, out_path, camera_list, path_to_project, switch):
    """
    Take the input XML file and exclude the cameras with the serials in the exclude list
    """
    tree = ET.parse(in_path)

    root = tree.getroot()
    if switch:
        for camera in root.find("cameras").findall("camera"):
            if camera.attrib.get("serial") in camera_list:
                root.find("cameras").remove(camera)
    else:
        for camera in root.find("cameras").findall("camera"):
            if camera.attrib.get("serial") not in camera_list:
                root.find("cameras").remove(camera)
    tree.write(out_path)
    with open(out_path, "r") as xml_file:
        xml_content = xml_file.read()
    file_name = os.path.split(out_path)[-1]
    with open(
        os.path.join(path_to_project, file_name.replace(".xml", ".qca.txt")), "w"
    ) as txt_file:
        txt_file.write("<?xml version='1.0' encoding='ASCII'?>\n")
        txt_file.write(xml_content)


if __name__ == "__main__":
    argspars = argparse.ArgumentParser()
    argspars.add_argument(
        "--in_path",
        default=r"./Gait Markerless 2.settings.xml",
        type=str,
        help="Path to the input XML file",
    )
    argspars.add_argument(
        "--out_path",
        default=r"./Gait Markerless 2.settings_new.xml",
        type=str,
        help="Path to the output XML file",
    )
    argspars.add_argument(
        "--exclude",
        nargs="+",
        default="None",
        type=str,
        help="List of serials to not exclude",
    )
    argspars.add_argument(
        "--path_to_project",
        default=r".\Data\experiments\new\LIHS\ROM2\calibration",
        type=str,
        help="List of serials to not exclude",
    )
    argspars.add_argument(
        "--not_exclude",
        nargs="+",
        default="all",
        type=str,
        help="List of serials to not exclude",
    )
    args = argspars.parse_args()
    camera_list = []
    switch = False
    if args.not_exclude:
        if "all" in args.not_exclude[0]:
            camera_list = []
        elif "," in args.not_exclude[0]:
            camera_list = args.not_exclude[0].split(",")
        else:
            camera_list = args.not_exclude
    elif args.exclude:
        switch = True
        if "None" in args.exclude[0]:
            camera_list = []
        elif "," in args.exclude[0]:
            camera_list = args.exclude[0].split(",")
        else:
            camera_list = args.exclude

    parseXML(args.in_path, args.out_path, camera_list, args.path_to_project, switch)
