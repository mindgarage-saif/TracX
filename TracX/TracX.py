import logging
import os
import shutil
from datetime import datetime

import cv2
from Pose2Sim.Utilities import bodykin_from_mot_osim

from TracX.core import Experiment
from TracX.core.analyze2d import process as process2d
from TracX.core.analyze3d import lift_2d_to_3d
from TracX.kinematics import run_kinematics


def process_mono2d(experiment: Experiment):
    if len(experiment.videos) == 0:
        raise ValueError("No videos found for experiment")

    video_path = experiment.videos[0]
    video_path = os.path.join(experiment.path, video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video {video_path} not found")

    # Run 2D pose estimation
    logging.info(f"Processing video {video_path}")
    config_dict = experiment.cfg.copy()
    config_dict["project"]["video_input"] = video_path
    config_dict["process"]["result_dir"] = experiment.path
    config_dict["post-processing"]["show_graphs"] = False
    process2d(config_dict)

    # Post-process paths
    logging.info("Cleaning up temporary files")
    save_dir = os.path.join(
        experiment.path, os.path.basename(video_path).split(".")[0] + "_Sports2D"
    )
    for file in os.listdir(save_dir):
        dest_dir = (
            experiment.pose2d_dir if file.endswith(".trc") else experiment.output_dir
        )
        dest_path = os.path.join(dest_dir, file)
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)
        shutil.move(os.path.join(save_dir, file), dest_dir)

    # Delete the temporary directory
    shutil.rmtree(save_dir)


def process_mono3d(experiment: Experiment):
    process_mono2d(experiment)

    logging.info("Lifting 2D poses to 3D")
    pose2d_files = [
        os.path.join(experiment.pose2d_dir, f)
        for f in os.listdir(experiment.pose2d_dir)
        if f.endswith(".trc") and "Sports2D" in f
    ]

    # Get the video resolution
    video_path = experiment.videos[0]
    video_path = os.path.join(experiment.path, video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video {video_path} not found")

    cap = cv2.VideoCapture(video_path)
    res_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    res_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    os.makedirs(experiment.pose3d_dir, exist_ok=True)
    for pose2d_file in pose2d_files:
        pose3d_file = os.path.join(
            experiment.pose3d_dir, os.path.basename(pose2d_file).replace("Sports2D", "")
        )
        pose3d_file = pose3d_file.replace(".trc", "_filt_butterworth.trc")
        logging.info(f"Lifting {pose2d_file} to {pose3d_file}")
        lift_2d_to_3d(pose2d_file, pose3d_file, res_w, res_h)

        # Remove original 2D pose file
        os.remove(pose2d_file)

        # # Perform filtering
        # logging.info("Filtering 3D poses")
        # Pose2Sim.filtering(experiment.cfg)


def process_multi3d(experiment: Experiment):
    # FIXME: Move processing out of the Experiment class
    experiment.process()


def process(name: str):
    try:
        experiment = Experiment.open(name)
    except FileNotFoundError:
        logging.error(f"Experiment {name} not found.")
        return

    if len(experiment.videos) == 0:
        logging.info(f"No videos found for experiment {experiment.name}")
        return

    currentDateAndTime = datetime.now()
    logging.info(
        "---------------------------------------------------------------------"
    )
    if experiment.monocular:
        if experiment.is_2d:
            logging.info(f"Processing 2D single-camera experiment '{experiment.name}'")
            process_fun = process_mono2d
        else:
            logging.info(f"Processing 3D single-camera experiment '{experiment.name}'")
            process_fun = process_mono3d
    else:
        logging.info(f"Processing 3D multi-camera experiment '{experiment.name}'")
        process_fun = process_multi3d

    logging.info(f"On {currentDateAndTime.strftime('%A %d. %B %Y, %H:%M:%S')}")
    logging.info(
        "---------------------------------------------------------------------"
    )

    # Run the processing function
    process_fun(experiment)


def kinematics(name: str, overwrite: bool = False):
    try:
        experiment = Experiment.open(name)
        pose_model = experiment.cfg["pose"]["pose_model"]
    except FileNotFoundError:
        logging.error(f"Experiment {name} not found.")
        return

    # Find the motion file
    motion_file = experiment.get_motion_file()
    if motion_file is None:
        logging.error(
            "Process the experiment to create the motion file before kinematics computation"
        )
        return

    # Skip kinematics if the mot and scaled model files already exist
    output_dir = experiment.output_dir
    mot_file = os.path.join(output_dir, "ik.mot")
    scaled_model_file = os.path.join(output_dir, "scaled_model.osim")
    if not overwrite and os.path.exists(mot_file) and os.path.exists(scaled_model_file):
        logging.info("Kinematics files already exist. Skipping kinematics computation")
        return output_dir, mot_file, scaled_model_file

    currentDateAndTime = datetime.now()
    logging.info(
        "---------------------------------------------------------------------"
    )
    logging.info("OpenSim Kinematics")
    logging.info(f"On {currentDateAndTime.strftime('%A %d. %B %Y, %H:%M:%S')}")
    logging.info(f"Motion file: {motion_file}")
    logging.info(f"Pose model: {pose_model}")
    logging.info(f"Output directory: {experiment.output_dir}")
    logging.info(
        "---------------------------------------------------------------------"
    )

    # TODO: Read time range from the config file
    output, mot, scaled_model = run_kinematics(
        motion_file=motion_file,
        output_dir=experiment.output_dir,
        pose_model=pose_model,
        time_range=None,  # Use the entire motion file
    )

    with_blender = False  # TODO: Implement Blender integration
    if with_blender:
        bodykin_from_mot_osim.bodykin_from_mot_osim_func(
            mot,
            scaled_model,
            os.path.join(output, "bodykin.csv"),
        )

    return output, mot, scaled_model
