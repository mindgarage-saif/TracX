import json
from time import strftime
from typing import List, Optional

from mocap.core import Experiment


def create_experiment(
    video_files: List[str],
    calibration_file: str,
    experiment_name: Optional[str] = None,
) -> Experiment:
    # Create a new project.
    experiment_name = experiment_name or strftime("%Y%m%d_%H%M%S")
    experiment = Experiment(experiment_name, create=True)

    # Add the video files.
    for video_file in video_files:
        experiment.add_video(video_file)

    # Make sure that at least one video file was added.
    if experiment.num_videos == 0:
        raise ValueError("No supported video files found")

    # Add the camera calibration file.
    experiment.set_camera_parameters(calibration_file)

    return experiment


def execute_pipeline(
    video_files: List[str],
    calibration_file: str,
    correct_rotation=True,
    do_synchronization=False,
    use_marker_augmentation=False,
    visualization_mode="opensim",
    visualization_args=dict(),
    experiment_name: Optional[str] = None,
):
    """Run the full pipeline for a given set of video files and calibration file.

    Args:
        video_files (List[str]): List of paths to video files.
        calibration_file (str): Path to the camera calibration file.
        correct_rotation (bool, optional): Whether to rotate the 2D poses. Defaults to False.
        do_synchronization (bool, optional): Whether to run synchronization. Defaults to False.
        use_marker_augmentation (bool, optional): Whether to use marker augmentation. Defaults to False.
        opensim (bool, optional): Whether to run OpenSim processing. Defaults to True.
        blender (bool, optional): Whether to run Blender processing. Defaults to False.
        experiment_name (Optional[str], optional): Name of the experiment. Defaults to None.

    Raises:
        ValueError: If the config file is invalid or not a .toml file.

    Note:
        Assumes camera calibration to be in QCA camera format. It doesn't matter if it is in XML file
        format or txt file format. But internally it has to be in QCA format.
    """
    # Initialize the experiment
    print("Initializing experiment...")
    experiment: Experiment = create_experiment(
        video_files,
        calibration_file,
        experiment_name=experiment_name,
    )
    print(f"Created {experiment} with {experiment.num_videos} video(s)")
    print(f"Experiment configuration: {json.dumps(experiment.cfg, indent=4)}")

    experiment.process(
        correct_rotation=correct_rotation,
        do_synchronization=do_synchronization,
        use_marker_augmentation=use_marker_augmentation,
    )

    experiment.visualize(
        mode=visualization_mode,
        **visualization_args,
    )
