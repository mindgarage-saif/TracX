import json
import os
import shutil
from distutils.dir_util import copy_tree
from typing import Optional

import cv2
import toml
from easydict import EasyDict as edict
from Pose2Sim import Pose2Sim
from Pose2Sim.Utilities import bodykin_from_mot_osim

from mocap.constants import (
    APP_ASSETS,
    APP_PROJECTS,
    OPENSIM_DIR,
    SUPPORTED_VIDEO_FORMATS,
)
from mocap.rendering import StickFigureRenderer, create_opensim_vis

from .motion import MotionSequence
from .pose import PoseTracker2D, lift_to_3d
from .rotation import rotate_video_monocular, rotate_videos, unrotate_pose2d


class Experiment:
    def __init__(self, name, create=True, base_dir=APP_PROJECTS) -> None:
        self.name = name
        self.path = os.path.abspath(os.path.join(base_dir, name))
        self.config_file = os.path.join(self.path, "Config.toml")
        self.videos_dir = os.path.join(self.path, "videos")
        self.pose2d_dir = os.path.join(self.path, "pose")
        self.pose3d_dir = os.path.join(self.path, "pose-3d")
        self.output_dir = os.path.join(self.path, "output")
        self.calibration_dir = os.path.join(self.path, "calibration")
        self.calibration_file = os.path.join(
            self.calibration_dir,
            "camera_parameters.qca.txt",
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
        if os.path.exists(os.path.join(APP_PROJECTS, "experiments.json")):
            with open(os.path.join(APP_PROJECTS, "experiments.json")) as f:
                data = json.load(f)
            return sorted(data["experiments"], key=lambda x: x["name"])
        return []
        return sorted(
            [
                name
                for name in os.listdir(APP_PROJECTS)
                if os.path.isdir(os.path.join(APP_PROJECTS, name))
            ],
        )

    @staticmethod
    def open(name):
        return Experiment(name, create=False)

    @staticmethod
    def from_path(path):
        return Experiment(
            os.path.basename(path),
            create=False,
            base_dir=os.path.dirname(path),
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
        os.makedirs(self.videos_dir, exist_ok=True)
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
                "Invalid calibration file format. We except a Qualisys calibration file in XML format.",
            )

        shutil.copy(params_file, self.calibration_file)

    def get_camera_parameters(self):
        return self.calibration_file if os.path.exists(self.calibration_file) else None

    def process(
        self,
        correct_rotation=True,
        use_marker_augmentation=False,
        mode="multiview",
        engine="Pose2Sim",
        pose2d_model="DFKI_Body43",
        lifting_model="Baseline",
        lifting_kwargs={},
    ):
        assert mode in [
            "multiview",
            "monocular",
        ], "Invalid mode. Use 'multiview' or 'monocular'."
        assert engine in [
            "Pose2Sim",
            "Custom",
        ], "Invalid engine. Use 'Pose2Sim' or 'Custom'."

        # If monocular mode, set Custom engine and set pose model to Pose2Sim_Halpe26
        if mode == "monocular":
            print(
                "Monocular mode selected. Setting engine to 'Custom' and model to 'Pose2Sim_Halpe26'"
            )
            engine = "Custom"
            pose2d_model = "Pose2Sim_Halpe26"

        # Change the working directory to the project directory.
        cwd = os.getcwd()
        os.chdir(self.path)

        if not self.has_videos():
            raise ValueError("No videos found in the project directory.")

        if correct_rotation:
            rotated_dir = os.path.join(self.path, self.videos_dir + "_rotated")
            if not os.path.exists(rotated_dir):
                rotation = lifting_kwargs["rotation"] = None
                if rotation == None:
                    rotate_video_monocular(self.videos, rotated_dir, rotation)
                elif mode != "monocular":
                    rotate_videos(self.videos, rotated_dir, self.calibration_file)
                else:
                    raise ValueError("Rotation angle is required for monocular mode.")
            else:
                print("Rotated videos already exist. Skipping rotation...")

            # Rename the videos directories to use the rotated videos
            if os.path.exists(self.videos_dir) and os.path.exists(rotated_dir):
                os.rename(self.videos_dir, self.videos_dir + "_original")
                os.rename(rotated_dir, self.videos_dir)

        # Set video format and overwrite flag
        # TODO: Read these from self.cfg
        videos_format = os.path.splitext(self.videos[0])[-1].lower()
        overwrite = False

        # Execute the 2D pose estimation
        print("Executing 2D pose estimatioan...")
        res_w, res_h = 0, 0
        if engine == "Pose2Sim":
            PoseTracker2D.estimateDefault()
        else:
            if pose2d_model == "DFKI_Body43":
                res_w, res_h, _ = PoseTracker2D.estimateBodyWithSpine(
                    videos=self.videos_dir,
                    save_dir=self.pose2d_dir,
                    video_format=videos_format,
                    overwrite=overwrite,
                )
            elif pose2d_model == "Pose2Sim_Halpe26":
                res_w, res_h, _ = PoseTracker2D.estimateBodyWithFeet(
                    videos=self.videos_dir,
                    save_dir=self.pose2d_dir,
                    video_format=videos_format,
                    overwrite=overwrite,
                )
            else:
                raise ValueError(f"Unsupported custom pose model '{pose2d_model}'")

        # Unrotate the 2D poses
        if correct_rotation:
            # Restore the original videos
            os.rename(self.videos_dir, self.videos_dir + "_rotated")
            os.rename(self.videos_dir + "_original", self.videos_dir)

            print("Rotating 2D poses back...")
            unrotate_pose2d(self.pose2d_dir, self.calibration_file)

        # 2D-to-3D Lifting in Monocular Mode
        if mode == "monocular":
            print("Lifting 2D poses to 3D...")
            if lifting_model == "Baseline":
                if res_w == 0 or res_h == 0:
                    raise ValueError(
                        "Invalid resolution. Something went wrong during 2D pose estimation."
                    )

                # Lift the 2D poses to 3D
                model_path = os.path.join(
                    APP_ASSETS, "models", "lifting", "baseline.onnx"
                )
                lift_to_3d(model_path, self.pose2d_dir, self.pose3d_dir, res_w, res_h)
            else:
                raise ValueError(f"Unsupported lifting model '{lifting_model}'")

        # Triangulation in Multiview Mode
        else:
            print("Triangulating 2D poses to 3D...")
            Pose2Sim.calibration()
            try:
                # Pose2Sim.synchronization()
                Pose2Sim.personAssociation()
            except Exception as e:
                print(e)
                raise e
            Pose2Sim.triangulation()
            Pose2Sim.filtering()
            if use_marker_augmentation:
                Pose2Sim.markerAugmentation()

        # Restore the working directory
        os.chdir(cwd)

    def get_motion_file(self) -> Optional[str]:
        trc_files = [
            f
            for f in os.listdir(self.pose3d_dir)
            if f.endswith("_filt_butterworth.trc")
        ]
        if len(trc_files) == 0:
            return None
        return os.path.join(self.pose3d_dir, trc_files[0])

        # FIXME: Monoocular mode
        pose_3d = [f for f in os.listdir(self.pose3d_dir) if f.endswith("data.json")]
        if len(pose_3d) == 0:
            return None
        return os.path.join(self.pose3d_dir, pose_3d[0])

    @property
    def log_file(self):
        return os.path.join(self.path, "logs.log")

    def read_skeleton(self):
        file = toml.load(self.config_file)
        return file["pose"]["pose_model"]

    def _visualize_naive(self, motion_file):
        # Create a side-by-side visualization using OpenCV
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        if os.path.exists(animation_file):
            return animation_file

        # Find FPS of the first camera video
        video_file = self.videos[0]
        video = cv2.VideoCapture(video_file)
        fps = video.get(cv2.CAP_PROP_FPS)
        video.release()
        skeleton = self.read_skeleton()

        # Create the visualization
        animation_file = os.path.join(self.output_dir, "stick_animation.mp4")
        motion_data = MotionSequence.from_pose2sim_trc(motion_file, skeleton)
        renderer = StickFigureRenderer(motion_data, animation_file)
        renderer.render(fps=fps)

        # FIXME: Monoocular mode
        # motion_data = MotionSequence.from_monocular_json(motion_file, fps)
        # renderer = StickFigureRenderer(
        #     motion_data,
        #     animation_file,
        #     monocular=True,
        #     elev=-165,
        #     azim=155,
        #     vertical_axis="y",
        # )

        return animation_file

    def _visualize_opensim(self, motion_file, with_blender=False):
        copy_tree(
            os.path.join(OPENSIM_DIR, "..", "geometry"),
            os.path.join(self.output_dir, "Geometry"),
        )
        output, mot, scaled_model = create_opensim_vis(
            trc=motion_file,
            experiment_dir=self.path,
            scaling_time_range=[0.5, 1.0],
            ik_time_range=None,
        )

        if with_blender:
            bodykin_from_mot_osim.bodykin_from_mot_osim_func(
                mot,
                scaled_model,
                os.path.join(output, "bodykin.csv"),
            )

        return output, mot, scaled_model

    def visualize(self, mode="naive", **kwargs):
        """Visualize the results of the experiment.

        Args:
            mode (str): The visualization mode. Supported modes include ['naive', 'mesh', mixamo', 'opensim'].
            **kwargs: Additional keyword arguments to pass to the visualization function for the selected mode.
                      See the documentation of the corresponding visualization function for more details.

        """
        motion_file = self.get_motion_file()
        if motion_file is None:
            raise ValueError(
                "Call the .process() method first before visualizing the results.",
            )

        # Check the visualization mode
        supported_modes = ["naive", "mesh", "mixamo", "opensim"]
        if mode == "naive":
            return self._visualize_naive(motion_file, **kwargs)
        if mode == "opensim":
            return self._visualize_opensim(motion_file, **kwargs)
        raise ValueError(
            f"Unsupported visualization mode '{mode}'. Use one of {supported_modes}",
        )

    def __str__(self):
        return f"Experiment(name={self.name}, path={self.path})"
