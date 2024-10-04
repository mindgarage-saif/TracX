import os
import xml.etree.ElementTree as ET

import opensim

from mocap.constants import OPENSIM_DIR


def parse_osim_file(file_path):
    """
    Parse the osim file to extract marker names and locations.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    markerset = root.find(".//MarkerSet")
    if markerset is None:
        raise ValueError("MarkerSet not found in the file")

    markers = []
    for marker in markerset.findall(".//Marker"):
        name = marker.get("name")
        location_text = marker.find("location").text.replace(",", ".")
        location = list(map(float, location_text.split()))
        markers.append({"name": name, "location": location})

    return markers


def do_scaling(path_to_scaling):
    opensim.ScaleTool(path_to_scaling).run()
    print("Scaling has been completed")


def do_ik(path_to_ik_setup):
    opensim.InverseKinematicsTool(path_to_ik_setup).run()
    print("Inverse Kinematics has been completed")


def adapt_scaling_xml(
    setup_file,
    trc_file,
    time_range,
    output_dir,
    model_path,
):
    # Read the file
    tree = ET.parse(setup_file)
    root = tree.getroot()

    # Change path to the trc file
    for item in root.iter("marker_file"):
        item.text = trc_file

    # Change the time range
    for item in root.iter("time_range"):
        item.text = str(time_range[0]) + "," + str(time_range[1])

    # Change the output model file
    for item in root.iter("output_model_file"):
        item.text = os.path.abspath(os.path.join(output_dir, "scaled_model.osim"))

    for item in root.iter("model_file"):
        item.text = model_path

    # for item in root.iter('marker_set_file'):
    #     item.text = os.path.join(output_dir,'marker_set.xml')

    # Write the new file
    filename = os.path.basename(setup_file)
    outfile = os.path.join(output_dir, filename)
    tree.write(outfile)


def adapt_ik_xml(setup_file, trc_file, output_dir, time_range=None):
    # Read the file
    tree = ET.parse(setup_file)
    root = tree.getroot()

    # Change path to the trc file
    for item in root.iter("marker_file"):
        item.text = trc_file

    # Change the time range
    if time_range is not None:
        for item in root.iter("time_range"):
            item.text = str(time_range[0]) + " " + str(time_range[1])
    # else:
    #     for item in root.iter("time_range"):
    #         item.text = " "

    for item in root.iter("output_motion_file"):
        item.text = os.path.abspath(os.path.join(output_dir, "ik.mot"))

    for item in root.iter("model_file"):
        item.text = os.path.join(output_dir, "scaled_model.osim")

    for item in root.iter("results_directory"):
        item.text = output_dir

    filename = os.path.basename(setup_file)
    tree.write(os.path.join(output_dir, filename))


def create_opensim_vis(
    trc,
    experiment_dir,
    scaling_time_range=[0.5, 1.0],
    model="Model.osim",
    ik_file="IK_Setup.xml",
    scaling_file="Scaling_Setup.xml",
    ik_time_range=None,
):
    opensim_dir = os.path.join(experiment_dir, "..", "..", OPENSIM_DIR)

    model_path = os.path.join(opensim_dir, model)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")

    scaling_setup_file = os.path.join(opensim_dir, scaling_file)
    if not os.path.exists(scaling_setup_file):
        raise FileNotFoundError(f"Scaling file {scaling_setup_file} not found")

    ik_setup_path = os.path.join(opensim_dir, ik_file)
    if not os.path.exists(ik_setup_path):
        raise FileNotFoundError(f"IK file {ik_setup_path} not found")

    output_dir = os.path.join(experiment_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Scaling
    scaling_file = os.path.basename(scaling_file)
    adapt_scaling_xml(
        setup_file=scaling_setup_file,
        trc_file=trc,
        time_range=scaling_time_range,
        output_dir=output_dir,
        model_path=model_path,
    )
    do_scaling(os.path.join(output_dir, scaling_file))

    # Inverse Kinematics
    adapt_ik_xml(ik_setup_path, trc, output_dir, ik_time_range)
    do_ik(os.path.join(output_dir, ik_file))

    print("The results can be found in: ", output_dir)
    return (
        output_dir,
        os.path.join(output_dir, "ik.mot"),
        os.path.join(output_dir, "scaled_model.osim"),
    )
