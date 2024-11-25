import logging
import os
import shutil
from datetime import datetime

import cv2

from mocap.core import Experiment
from mocap.core.analyze2d import process as process2d
from mocap.core.analyze3d import lift_2d_to_3d
from mocap.rendering.opensim import create_osim_models


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
    logging.info("Updating paths")
    save_dir = os.path.join(
        experiment.path, os.path.basename(video_path).split(".")[0] + "_Sports2D"
    )
    for file in os.listdir(save_dir):
        dest_dir = (
            experiment.pose3d_dir if file.endswith(".trc") else experiment.output_dir
        )
        dest_path = os.path.join(dest_dir, file)
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)
        shutil.move(os.path.join(save_dir, file), dest_dir)

    # Delete the temporary directory
    logging.info("Cleaning up")
    shutil.rmtree(save_dir)


def process_mono3d(experiment: Experiment):
    process_mono2d(experiment)

    logging.info("Lifting 2D poses to 3D")
    pose2d_files = [
        os.path.join(experiment.pose3d_dir, f)
        for f in os.listdir(experiment.pose3d_dir)
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

        logging.info("Creating OpenSim models")
        create_osim_models(
            trc=pose3d_file,
            experiment_dir=experiment.path,
        )


def process_multi3d(experiment: Experiment):
    pass


def process(name: str):
    try:
        experiment = Experiment.open(name)
    except FileNotFoundError:
        print(f"Experiment {name} not found.")
        return

    # Setup logging
    root_dir = experiment.path
    logfile = os.path.join(root_dir, "logs.txt")
    with open(logfile, "a+") as log_f:
        pass
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        force=True,
        handlers=[
            logging.handlers.TimedRotatingFileHandler(logfile, when="D", interval=7),
            logging.StreamHandler(),
        ],
    )

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
            process_fun = process_mono3d
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

    logging.shutdown()
