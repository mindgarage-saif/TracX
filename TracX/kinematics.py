import logging
import os
import shutil
import xml.etree.ElementTree as ET
from distutils.dir_util import copy_tree

import opensim
from Pose2Sim.kinematics import read_trc

from TracX.constants import OPENSIM_FILES, OPENSIM_GEOMETRY


def adapt_scaling_setup(
    scaling_file: str,
    marker_file: str,
    model_file: str,
    output_dir: str,
    time_range: tuple,
):
    """ Save a copy of the scaling setup file adapted to the current experiment.

    Args:
        setup_file (str): Path to the original scaling setup file.
        marker_file (str): Path to the TRC file containing the marker positions used for measurement-based scaling.
        model_file (str): Path to the model file (.osim) for the unscaled model.
        output_dir (str): Path to the output directory where the adapted setup file will be saved.
        time_range (tuple): Time range over which to average marker-pair distances in the marker file (.trc) for measurement-based scaling.
    """
    # TODO: Read hardcoded values below from the experiment object
    scaling_parameters = dict(
        # Mass of the subject in kg. Subject-specific model generated by scaling step will have this total mass.
        mass=69,
        # Height of the subject in mm. For informational purposes only (not used by scaling).
        height=1.74,
        # Age of the subject in years. For informational purposes only (not used by scaling).
        age=28,
        # Model file (.osim) for the unscaled model. This is the model that will be scaled to match the experimental data. Scaling is done based on distances between model markers compared to the same distances between the corresponding experimental markers.
        model_file=model_file,
        # TRC file (.trc) containing the marker positions used for measurement-based scaling. This is usually a static trial, but doesn't need to be.  The marker-pair distances are computed for each time step in the TRC file and averaged across the time range.
        marker_file=os.path.basename(marker_file),
        # Time range over which to average marker-pair distances in the marker file (.trc) for measurement-based scaling
        time_range=str(time_range[0]) + "," + str(time_range[1]),
        # Name of the motion file (.mot) written after marker relocation.
        output_motion_file=os.path.join(output_dir, "scaled_motion.mot"),
        # Output OpenSim model file (.osim) after scaling and maker placement.
        output_model_file=os.path.join(output_dir, "scaled_model.osim"),
        # Output marker set containing the new marker locations after markers have been placed.
        output_marker_file=os.path.join(output_dir, "scaled_markers.trc"),
        # Maximum amount of movement allowed in marker data when averaging frames of the static trial. A negative value means there is not limit.
        max_marker_movement=-1,
    )

    # Adapt the setup file
    tree = ET.parse(scaling_file)
    root = tree.getroot()
    for k, v in scaling_parameters.items():
        for item in root.iter(k):
            item.text = str(v)

    # Save the adapted setup file
    adapted_scaling_file = os.path.join(output_dir, "Scaling_Setup.xml")
    tree.write(adapted_scaling_file)

    return adapted_scaling_file


def adapt_ik_setup(
    ik_file: str,
    marker_file,
    output_dir,
    time_range
):
    # TODO: Read hardcoded values below from the experiment object
    ik_parameters = dict(
        results_directory=output_dir,
        marker_file=os.path.basename(marker_file),
        output_motion_file=os.path.join(output_dir, "ik.mot"),
        model_file=os.path.join(output_dir, "scaled_model.osim"),
        time_range=str(time_range[0]) + " " + str(time_range[1]),
    )

    # Adapt the setup file
    tree = ET.parse(ik_file)
    root = tree.getroot()
    for k, v in ik_parameters.items():
        for item in root.iter(k):
            item.text = str(v)

    # Save the adapted setup file
    adapted_scaling_file = os.path.join(output_dir, "IK_Setup.xml")
    tree.write(adapted_scaling_file)

    return adapted_scaling_file


def run_kinematics(
    motion_file: str,
    output_dir: str,
    pose_model="HALPE_26",
    time_range=None,
):
    # Find OpenSim files
    logging.info("Finding OpenSim files...")
    osim_files = OPENSIM_FILES.get(pose_model, {})
    osim_model_file = osim_files.get("Model")
    osim_scaling_file = osim_files.get("Scaling_Setup")
    osim_ik_file = osim_files.get("IK_Setup")

    # Check if all required files are present
    required_files = [osim_model_file, osim_scaling_file, osim_ik_file]
    if not all(required_files) or not all(map(os.path.exists, required_files)):
        message = "Required OpenSim files not found, Check that the following files are present:"
        for f in required_files:
            message += f"\n- {f}"
        logging.error(message)
        raise FileNotFoundError(message)

    # Create output directory (if not present)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Copy model and OpenSim geometry files to the output directory
    logging.info("Copying OpenSim files to the output directory...")
    model_file = os.path.abspath(os.path.join(output_dir, "model.osim"))
    shutil.copy(osim_model_file, model_file)
    copy_tree(OPENSIM_GEOMETRY, os.path.join(output_dir, "Geometry"))

    # Copy motion file to the output directory
    marker_file = os.path.join(output_dir, os.path.basename(motion_file))
    logging.info(f"Copying motion file to the output directory: {marker_file}")
    shutil.copy(motion_file, marker_file)

    # Read time range from motion file if not provided
    if time_range is None:
        logging.info("Reading time range from the motion file...")
        time_col = read_trc(motion_file)[2]  # Pandas Column object (take first and last values)
        time_range = (time_col.iloc[0], time_col.iloc[-1])

    # If duration is longer than 10 seconds, use the middle 10 seconds for scaling
    duration = time_range[1] - time_range[0]
    if duration > 10:
        logging.info("Duration of the motion file is longer than 10 seconds, using the middle 10 seconds for scaling...")
        scaling_time_range = (time_range[0] + duration / 2 - 5, time_range[0] + duration / 2 + 5)
    else:
        scaling_time_range = time_range
    logging.info(f"Scaled time range: {scaling_time_range}")
    
    # Use the complete time range for IK
    ik_time_range = time_range
    logging.info(f"IK time range: {ik_time_range}")

    # Run OpenSim Scaling
    try:
        logging.info("Adapting scaling setup file to the current experiment...")
        scaling_file = adapt_scaling_setup(
            scaling_file=osim_scaling_file,
            marker_file=marker_file,
            model_file=model_file,
            output_dir=output_dir,
            time_range=scaling_time_range,
        )

        logging.info("Running OpenSim Scaling...")
        opensim.ScaleTool(scaling_file).run()
        logging.info("Scaling successfully completed")
    except Exception as e:
        logging.error("Scaling failed, aborting...")
        # TODO: Rollback changes
        raise e

    # Run OpenSim Inverse Kinematics
    try:
        logging.info("Adapting IK setup file to the current experiment...")
        ik_file = adapt_ik_setup(
            ik_file=osim_ik_file,
            marker_file=marker_file,
            output_dir=output_dir,
            time_range=ik_time_range,
        )

        logging.info("Running OpenSim Inverse Kinematics...")
        opensim.InverseKinematicsTool(ik_file).run()
        logging.info("Inverse Kinematics successfully completed")
    except Exception as e:
        logging.error("Inverse Kinematics failed, aborting...")
        # TODO: Rollback changes
        raise e
 
    # TODO: Integrate Inverse Dynamics when muscles are available

    return (
        output_dir,
        os.path.join(output_dir, "ik.mot"),
        os.path.join(output_dir, "scaled_model.osim"),
    )