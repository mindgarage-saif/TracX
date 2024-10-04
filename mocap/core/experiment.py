import os
import shutil
from typing import Optional

import cv2
import toml
from easydict import EasyDict as edict
from Pose2Sim import Pose2Sim
from Pose2Sim.Utilities import bodykin_from_mot_osim

from mocap.constants import APP_ASSETS, APP_PROJECTS, SUPPORTED_VIDEO_FORMATS
from mocap.rendering import StickFigureRenderer, create_opensim_vis

from .motion import MotionSequence
from .rotation import rotate_videos, unrotate_pose2d


class Experiment:
    def __init__(self, name, create=True, base_dir=APP_PROJECTS) -> None:
        self.name = name
        self.path = os.path.abspath(os.path.join(base_dir, name))
        self.videos_dir = os.path.join(self.path, "videos")
        self.pose2d_dir = os.path.join(self.path, "pose")
        self.pose3d_dir = os.path.join(self.path, "pose-3d")
        self.output_dir = os.path.join(self.path, "vis")
        self.calibration_dir = os.path.join(self.path, "calibration")
        self.calibration_file = os.path.join(
            self.calibration_dir, "camera_parameters.qca.txt"
        )
        self.config_file = os.path.join(self.path, "Config.toml")

        if create:
            try:
                # Create the project directories.
                self._makedirs()

                # Copy the default configuration file.
                default_config = os.path.join(APP_ASSETS, "defaults", "Config.toml")
                shutil.copy(default_config, self.config_file)
            except Exception:
                raise ValueError(f"Project '{name}' already exists.")
        elif not os.path.exists(self.config_file):
            raise ValueError(f"Project '{name}' is missing configuration file.")

        # Read the configuration file.
        self.cfg = toml.load(self.config_file)
        self.cfg = edict(self.cfg)

    @staticmethod
    def list():
        return sorted(
            [
                name
                for name in os.listdir(APP_PROJECTS)
                if os.path.isdir(os.path.join(APP_PROJECTS, name))
            ]
        )

    @staticmethod
    def open(name):
        return Experiment(name, create=False)

    @staticmethod
    def from_path(path):
        return Experiment(
            os.path.basename(path), create=False, base_dir=os.path.dirname(path)
        )

    def _makedirs(self):
        os.makedirs(self.path)
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.pose2d_dir, exist_ok=True)
        os.makedirs(self.pose3d_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.calibration_dir, exist_ok=True)

    @property
    def videos(self) -> list:
        return [
            os.path.join(self.videos_dir, name)
            for name in sorted(os.listdir(self.videos_dir))
            if os.path.isfile(os.path.join(self.videos_dir, name))
            and os.path.splitext(name)[-1].lower() in SUPPORTED_VIDEO_FORMATS
        ]

    @property
    def num_videos(self):
        return len(self.videos)

    def add_video(self, video_path, move=False) -> bool:
        video_name = os.path.basename(video_path)
        video_fmt = os.path.splitext(video_name)[-1].lower()
        if video_fmt not in SUPPORTED_VIDEO_FORMATS:
            return False

        video_dest = os.path.join(self.videos_dir, video_name)
        if move:
            os.rename(video_path, video_dest)
        else:
            shutil.copy(video_path, video_dest)

        return True

    def has_videos(self):
        return self.num_videos > 0

    def set_camera_parameters(self, params_file):
        if params_file.split(".")[-1].lower() != "xml":
            raise ValueError(
                "Invalid calibration file format. We except a Qualisys calibration file in XML format."
            )

        shutil.copy(params_file, self.calibration_file)

    def get_camera_parameters(self):
        return self.calibration_file if os.path.exists(self.calibration_file) else None

    def process(
        self,
        correct_rotation=True,
        do_synchronization=False,
        use_marker_augmentation=False,
    ):
        # Change the working directory to the project directory.
        cwd = os.getcwd()
        os.chdir(self.path)

        if not self.has_videos():
            raise ValueError("No videos found in the project directory.")

        if correct_rotation:
            rotated_dir = os.path.join(self.path, self.videos_dir + "_rotated")
            if not os.path.exists(rotated_dir):
                rotate_videos(self.videos, rotated_dir, self.calibration_file)
            else:
                print("Rotated videos already exist. Skipping rotation...")

            # Rename the videos directories to use the rotated videos
            if os.path.exists(self.videos_dir) and os.path.exists(rotated_dir):
                os.rename(self.videos_dir, self.videos_dir + "_original")
                os.rename(rotated_dir, self.videos_dir)

        # Execute the 2D pose estimation
        print("Executing 2D pose estimatioan...")
        Pose2Sim.poseEstimation()

        # Unrotate the 2D poses
        if correct_rotation:
            # Restore the original videos
            os.rename(self.videos_dir, self.videos_dir + "_rotated")
            os.rename(self.videos_dir + "_original", self.videos_dir)

            print("Rotating 2D poses back...")
            unrotate_pose2d(self.pose2d_dir, self.calibration_file)

        # Triangulate the 2D poses to 3D
        print("Triangulating 2D poses to 3D...")
        Pose2Sim.calibration()
        Pose2Sim.personAssociation()
        if do_synchronization:
            Pose2Sim.synchronization()
        Pose2Sim.triangulation()
        Pose2Sim.filtering()
        if use_marker_augmentation:
            Pose2Sim.markerAugmentation()

        # Restore the working directory
        os.chdir(cwd)

    def _find_trc_file(self) -> Optional[str]:
        trc_files = [
            f
            for f in os.listdir(self.pose3d_dir)
            if f.endswith("_filt_butterworth.trc")
        ]
        if len(trc_files) == 0:
            return None
        return os.path.join(self.pose3d_dir, trc_files[0])

    def _visualize_naive(self, motion_file):
        # Find FPS of the first camera video
        video_file = self.videos[0]
        video = cv2.VideoCapture(video_file)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()

        # Create the visualization
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        motion_data = MotionSequence.from_pose2sim_trc(motion_file)
        renderer = StickFigureRenderer(motion_data, animation_file)
        renderer.render()

        # Create a side-by-side visualization using OpenCV
        path = os.path.join(self.output_dir, "side_by_side.mp4")

        # Read the animation video
        anim = cv2.VideoCapture(animation_file)

        # Read the original video
        video = cv2.VideoCapture(video_file)

        # Get the video dimensions
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (width * 2, height)

        # Create the output video
        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

        while True:
            ret1, frame1 = video.read()
            ret2, frame2 = anim.read()

            if not ret1 or not ret2:
                break

            frame1 = cv2.resize(frame1, (width, height))
            frame2 = cv2.resize(frame2, (width, height))

            # Concatenate the frames
            frame = cv2.hconcat([frame1, frame2])

            # Write the frame
            out.write(frame)

        # Release the video objects
        video.release()
        anim.release()
        out.release()

        return path

    def _visualize_mesh(self, motion_file):
        pass

    def _visualize_mixamo(self, motion_file):
        pass

    def _visualize_opensim(self, motion_file, with_blender=False):
        from distutils.dir_util import copy_tree

        # copy_tree(os.path.join(opensim_dir,'geometry'), os.path.join(output,'Geometry'))
        output, mot, scaled_model = create_opensim_vis(
            trc=motion_file,
            experiment_dir=self.path,
            scaling_time_range=[0.5, 1.0],
            ik_time_range=None,
        )

        if with_blender:
            bodykin_from_mot_osim.bodykin_from_mot_osim_func(
                mot, scaled_model, os.path.join(output, "bodykin.csv")
            )

        return output, mot, scaled_model

    def visualize(self, mode="naive", **kwargs):
        """Visualize the results of the experiment.

        Args:
            mode (str): The visualization mode. Supported modes include ['naive', 'mesh', mixamo', 'opensim'].
            **kwargs: Additional keyword arguments to pass to the visualization function for the selected mode.
                      See the documentation of the corresponding visualization function for more details.
        """
        trc_file = self._find_trc_file()
        if trc_file is None:
            raise ValueError(
                "Call the .process() method first before visualizing the results."
            )

        # Check the visualization mode
        supported_modes = ["naive", "mesh", "mixamo", "opensim"]
        if mode == "naive":
            return self._visualize_naive(trc_file, **kwargs)
        elif mode == "mesh":
            return self._visualize_mesh(trc_file, **kwargs)
        elif mode == "mixamo":
            return self._visualize_mixamo(trc_file, **kwargs)
        elif mode == "opensim":
            return self._visualize_opensim(trc_file, **kwargs)
        else:
            raise ValueError(
                f"Unsupported visualization mode '{mode}'. Use one of {supported_modes}"
            )

    def __str__(self):
        return f"Experiment(name={self.name}, path={self.path})"
