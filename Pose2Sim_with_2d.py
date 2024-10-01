import argparse
import glob
import os
import shutil
from time import strftime
from typing import List, Optional

from Pose2Sim import Pose2Sim
from Pose2Sim.Utilities import bodykin_from_mot_osim

from util.OpenSim_create import create_opensim
from util.rotate2dBack import *
from util.rotator import rotate as rotate_videos


def triangulate(
    experiment_dir,
    do_synchronization=False,
    use_marker_augmentation=False,
):
    cwd = os.getcwd()
    os.chdir(experiment_dir)
    Pose2Sim.calibration()
    Pose2Sim.personAssociation()
    if do_synchronization:
        Pose2Sim.synchronization()
    Pose2Sim.triangulation()
    Pose2Sim.filtering()
    if use_marker_augmentation:
        Pose2Sim.markerAugmentation()
    os.chdir(cwd)

def estimate_pose2d(experiment_dir):
    Pose2Sim.poseEstimation(experiment_dir)


def init_experiment(
    video_files: List[str],
    calibration_file: str,
    rotate: bool = False,
    experiment_dir: str = "./experiments",
    experiment_name: Optional[str] = None,
):
    # Filter out unsupported video formats
    supported_formats = [".mp4", ".avi"]
    video_files = [
        v for v in video_files if any(v.endswith(fmt) for fmt in supported_formats)
    ]
    video_files = [v for v in video_files if os.path.exists(v)]
    if not video_files:
        raise ValueError("No supported video files found")

    # Create the experiment directory
    experiment_name = experiment_name or strftime("%Y%m%d_%H%M%S")
    experiment_dir = os.path.abspath(os.path.join(experiment_dir, experiment_name))
    videos_dir = os.path.join(experiment_dir, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    if rotate:
        rotate_videos(
            video_files,
            videos_dir,
            calibration_file,
        )
    else:
        for src in video_files:
            # Copy the video to the videos folder. This is necessary because Pose2Sim
            # assumes that the provided directory is the experiment directory with the
            # config file in it, and it does not natively allow specifying paths.
            dest = os.path.join(videos_dir, os.path.basename(src))
            shutil.copy(src, dest)

    return experiment_dir, experiment_name


def run_pipeline(
    video_files: List[str],
    calibration_file: str,
    config: str,
    rotate=False,
    opensim=True,
    blender=False,
    sync=False,
    marker_augmentation=False,
    experiment_dir: str = "./experiments",
    experiment_name: Optional[str] = None,
):
    """Run the full pipeline for a given set of video files and calibration file.

    Args:
        video_files (List[str]): List of paths to video files.
        calibration_file (str): Path to the camera calibration file.
        config (str): Path to the configuration file (must be a .toml file).
        rotate (bool, optional): Whether to rotate the 2D poses. Defaults to False.
        opensim (bool, optional): Whether to run OpenSim processing. Defaults to True.
        blender (bool, optional): Whether to run Blender processing. Defaults to False.
        experiment_dir (str, optional): Directory to store experiment results. Defaults to "./experiments".
        experiment_name (Optional[str], optional): Name of the experiment. Defaults to None.

    Raises:
        ValueError: If the config file is invalid or not a .toml file.

    Note:
        Assumes camera calibration to be in QCA camera format. It doesn't matter if it is in XML file
        format or txt file format. But internally it has to be in QCA format.
    """
    # Check if the config file is valid
    if not os.path.exists(config) or not config.lower().endswith(".toml"):
        raise ValueError("Invalid config file, should be a toml file")

    # Initialize the experiment
    print("Initializing experiment...")
    experiment_dir, experiment_name = init_experiment(
        video_files,
        calibration_file,
        rotate=rotate,
        experiment_dir=experiment_dir,
        experiment_name=experiment_name,
    )
    print(f"Experiment directory: {experiment_dir}")
    print(f"Experiment name: {experiment_name}")

    # Copy the config file to the experiment directory
    print("Copying config file...")
    shutil.copyfile(config, os.path.join(experiment_dir, "Config.toml"))

    # Copy the camera parameters to the calibration directory
    print("Copying camera parameters...")
    calibration_dir = os.path.join(experiment_dir, "calibration")
    os.makedirs(calibration_dir, exist_ok=True)
    shutil.copyfile(
        calibration_file,
        os.path.join(calibration_dir, "camera_parameters.qca.txt"),
    )

    # Execute the 2D pose estimation
    pose_dir = os.path.join(experiment_dir, "pose")
    pose_rotated_dir = os.path.join(experiment_dir, "pose_rotated")
    if not (os.path.exists(pose_dir) and os.path.exists(pose_rotated_dir)):
        print("Executing 2D pose estimation...")
        estimate_pose2d(experiment_dir)
        if rotate:
            print("Rotating 2D poses back...")
            rotate2dBack(pose_dir, calibration_file)
            shutil.move(pose_rotated_dir, pose_dir)

    # Triangulate the 2D poses to 3D
    print("Triangulating 2D poses to 3D...")
    triangulate(
        experiment_dir,
        do_synchronization=sync,
        use_marker_augmentation=marker_augmentation,
    )

    # Create OpenSim files
    print("Creating OpenSim files...")
    if opensim:
        pose3d_dir = os.path.join(experiment_dir, "pose-3d")
        if not os.path.exists(pose3d_dir):
            return

        trc_file = glob.glob(os.path.join(pose3d_dir, "*_filt_butterworth.trc"))[0]
        trc_file = os.path.basename(trc_file)
        trc_file = os.path.join("..", "pose-3d", trc_file)

        output, mot, scaled_model = create_opensim(
            trc=trc_file,
            experiment_dir=experiment_dir,
            scaling_time_range=[0.5, 1.0],
            ik_time_range=None,
        )

        if blender:
            bodykin_from_mot_osim.bodykin_from_mot_osim_func(
                mot, scaled_model, os.path.join(output, "bodykin.csv")
            )


if __name__ == "__main__":
    # argspaser = argparse.ArgumentParser()
    # argspaser.add_argument("--config",required=True,default=r"E:\Uni\MonocularSystems\HiWi\Data\experiments\new\LIHS\ROM2", type=str, help="Path to the config file")
    # argspaser.add_argument("--sync",default=False, type=bool, help="Sync the data")
    # argspaser.add_argument("--marker_augmentation",default=False, type=bool, help="Marker augmentation")
    # argspaser.add_argument("--camera_parameters",required=True,default=r"E:\Uni\MonocularSystems\HiWi\Gait Markerless 2.settings_new.xml", type=str, help="Path to the camera XML file")
    # argspaser.add_argument('--video_dir',required=True, type=str, help="Path to the video directory, which only contains the videos")
    # argspaser.add_argument('--rotate', default=False, type=bool, help="Should rotate the the videos")
    # argspaser.add_argument('--exp_name', default=None, type=str, help="Should sync the the videos")
    # argspaser.add_argument('--opensim', default=True, type=bool, help="Createse opensim files")
    # argspaser.add_argument('--blender', default=True, type=bool, help="Also returns the CSV files for blender")
    # args = argspaser.parse_args()

    # main(args.video_dir,args.camera_parameters,args.config,args.rotate,exp_name=args.exp_name,sync=args.sync,marker_augmentation=args.marker_augmentation,opensim=args.opensim,blender=args.blender)
    video_dir = [
        "~/Downloads/GAIT_1/Gait Markerless 1_Miqus_1_23087.avi",
        "~/Downloads/GAIT_1/Gait Markerless 1_Miqus_3_28984.avi",
        "~/Downloads/GAIT_1/Gait Markerless 1_Miqus_6_28983.avi",
    ]
    video_dir = [os.path.expanduser(vid) for vid in video_dir]
    camera = "Gait Markerless 2.settings_new.xml"
    config = "Config.toml"
    run_pipeline(video_dir, camera, config, True, opensim=True, blender=True)
    # assert args.config.endswith('.toml'), "The config file should be a toml file"
    # experiment_dir,exp_name = init_experiment(args.video_dir,args.camera_parameters,args.rotate,args.exp_name)
    # shutil.copyfile(args.config,os.path.join(experiment_dir,'Config.toml'))

    # if not (os.path.exists(os.path.join(experiment_dir,'pose')) and os.path.exists(os.path.join(experiment_dir,'pose_rotated'))):
    #     #pass
    #     execute_2d_detection(experiment_dir)
    #     rotate2dBack(os.path.join(experiment_dir,'pose'),args.camera_parameters)
    #     shutil.move(os.path.join(experiment_dir,'pose_rotated'), os.path.join(experiment_dir,'pose'))
    # #raise ValueError("Stop here")
    # os.makedirs(os.path.join(experiment_dir,'calibration'),exist_ok=True)
    # shutil.copyfile(args.camera_parameters,os.path.join(experiment_dir,'calibration','camera_parameters.qca.txt'))
    # execute_pose2sim_triangluation(experiment_dir,args.sync,args.marker_augmentation)
    # os.chdir(os.path.join(os.getcwd(),"../../"))
    # path_to_trc = glob.glob(os.path.join(experiment_dir,'pose-3d','*_filt_butterworth.trc'))[0]
    # if args.opensim:
    #     create_opensim(path_to_trc,exp_name)
